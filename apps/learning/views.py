from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from .models import LearningPath, Module, Content, UserProgress, UserEnrollment, Concept, StudentAnswer, Evaluation
from .serializers import (
    LearningPathSerializer, LearningPathListSerializer,
    ModuleSerializer, ModuleListSerializer,
    ContentSerializer, UserProgressSerializer,
    UserEnrollmentSerializer, ConceptSerializer
)
from .quiz_generator import QuizGenerator
from .services import AIEvaluator


class LearningPathViewSet(viewsets.ModelViewSet):
    """ViewSet for LearningPath model."""
    
    queryset = LearningPath.objects.filter(is_published=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            # Use detailed serializer if filtering by slug to get full content
            if self.request.query_params.get('slug'):
                return LearningPathSerializer
            return LearningPathListSerializer
        return LearningPathSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filter by slug
        slug = self.request.query_params.get('slug')
        if slug:
            queryset = queryset.filter(slug=slug)
        
        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                queryset = queryset.filter(tags__contains=[tag.strip()])
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.annotate(module_count=Count('modules'))
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll user in a learning path."""
        learning_path = self.get_object()
        
        enrollment, created = UserEnrollment.objects.get_or_create(
            user=request.user,
            learning_path=learning_path,
            defaults={'is_active': True}
        )
        
        if not created and not enrollment.is_active:
            enrollment.is_active = True
            enrollment.save()
        
        # Create or update overall progress tracker
        UserProgress.objects.get_or_create(
            user=request.user,
            learning_path=learning_path,
            module__isnull=True,
            content__isnull=True,
            defaults={'status': 'in_progress'}
        )
        
        # Increment enrollment count
        learning_path.total_enrollments += 1
        learning_path.save()
        
        return Response({
            'message': 'Successfully enrolled',
            'enrollment': UserEnrollmentSerializer(enrollment).data
        })
    
    @action(detail=True, methods=['post'])
    def unenroll(self, request, pk=None):
        """Unenroll user from a learning path."""
        learning_path = self.get_object()
        
        try:
            enrollment = UserEnrollment.objects.get(
                user=request.user,
                learning_path=learning_path
            )
            enrollment.is_active = False
            enrollment.save()
            return Response({'message': 'Successfully unenrolled'})
        except UserEnrollment.DoesNotExist:
            return Response(
                {'error': 'Not enrolled in this path'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get detailed progress for a learning path."""
        learning_path = self.get_object()
        
        progress_data = UserProgress.objects.filter(
            user=request.user,
            learning_path=learning_path
        )
        
        serializer = UserProgressSerializer(progress_data, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Module model."""
    
    queryset = Module.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ModuleListSerializer
        return ModuleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by learning path
        learning_path_id = self.request.query_params.get('learning_path')
        if learning_path_id:
            queryset = queryset.filter(learning_path_id=learning_path_id)
        
        return queryset.order_by('learning_path', 'order')


class ContentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Content model."""
    
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by module
        module_id = self.request.query_params.get('module')
        if module_id:
            queryset = queryset.filter(module_id=module_id)
        
        # Filter by content type
        content_type = self.request.query_params.get('type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        return queryset.order_by('module', 'order')
    
    @action(detail=True, methods=['post'])
    def generate_quiz(self, request, pk=None):
        """Generate a dynamic quiz for this content."""
        content = self.get_object()
        
        num_questions = int(request.data.get('num_questions', 5))
        difficulty = request.data.get('difficulty', 'intermediate')
        
        generator = QuizGenerator()
        quiz_data = generator.generate_quiz(
            content_id=content.id,
            num_questions=num_questions,
            difficulty=difficulty
        )
        
        if "error" in quiz_data:
            return Response(quiz_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response(quiz_data)

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """Submit an answer and get immersive feedback."""
        content = self.get_object()
        
        question = request.data.get('question')
        user_answer = request.data.get('user_answer')
        correct_answer = request.data.get('correct_answer')
        
        if not all([question, user_answer, correct_answer]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        generator = QuizGenerator()
        feedback = generator.evaluate_answer(
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer,
            context=content.text_content or ""
        )
        
        return Response(feedback)

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark content as complete."""
        content = self.get_object()
        
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            learning_path=content.module.learning_path,
            module=content.module,
            content=content,
            defaults={
                'status': 'completed',
                'progress_percentage': 100.0,
                'completed_at': timezone.now()
            }
        )
        
        if not created and progress.status != 'completed':
            progress.status = 'completed'
            progress.progress_percentage = 100.0
            progress.completed_at = timezone.now()
            progress.save()
        
        # Update module progress
        self._update_module_progress(request.user, content.module)
        
        # Update learning path progress
        self._update_learning_path_progress(request.user, content.module.learning_path)
        
        return Response({
            'message': 'Content marked as complete',
            'progress': UserProgressSerializer(progress).data
        })
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update progress for content."""
        content = self.get_object()
        
        progress_percentage = request.data.get('progress_percentage', 0)
        time_spent = request.data.get('time_spent_minutes', 0)
        score = request.data.get('score')
        
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            learning_path=content.module.learning_path,
            module=content.module,
            content=content,
            defaults={'status': 'in_progress'}
        )
        
        progress.progress_percentage = min(progress_percentage, 100.0)
        progress.time_spent_minutes += time_spent
        
        if score is not None:
            progress.score = score
            progress.attempts += 1
        
        if progress.progress_percentage >= 100.0:
            progress.status = 'completed'
            progress.completed_at = timezone.now()
        elif progress.status == 'not_started':
            progress.status = 'in_progress'
        
        progress.save()
        
        # Update higher-level progress
        self._update_module_progress(request.user, content.module)
        self._update_learning_path_progress(request.user, content.module.learning_path)
        
        return Response({
            'message': 'Progress updated',
            'progress': UserProgressSerializer(progress).data
        })
    
    def _update_module_progress(self, user, module):
        """Update module-level progress based on content progress."""
        module_contents = module.contents.all()
        total_contents = module_contents.count()
        
        if total_contents == 0:
            return
        
        completed_contents = UserProgress.objects.filter(
            user=user,
            module=module,
            content__in=module_contents,
            status='completed'
        ).count()
        
        progress_percentage = (completed_contents / total_contents) * 100
        
        module_progress, _ = UserProgress.objects.get_or_create(
            user=user,
            learning_path=module.learning_path,
            module=module,
            content__isnull=True
        )
        
        module_progress.progress_percentage = progress_percentage
        if progress_percentage >= 100.0:
            module_progress.status = 'completed'
            module_progress.completed_at = timezone.now()
        elif progress_percentage > 0:
            module_progress.status = 'in_progress'
        
        module_progress.save()
    
    def _update_learning_path_progress(self, user, learning_path):
        """Update learning path-level progress based on module progress."""
        modules = learning_path.modules.all()
        total_modules = modules.count()
        
        if total_modules == 0:
            return
        
        completed_modules = UserProgress.objects.filter(
            user=user,
            learning_path=learning_path,
            module__in=modules,
            content__isnull=True,
            status='completed'
        ).count()
        
        progress_percentage = (completed_modules / total_modules) * 100
        
        path_progress, _ = UserProgress.objects.get_or_create(
            user=user,
            learning_path=learning_path,
            module__isnull=True,
            content__isnull=True
        )
        
        path_progress.progress_percentage = progress_percentage
        if progress_percentage >= 100.0:
            path_progress.status = 'completed'
            path_progress.completed_at = timezone.now()
        elif progress_percentage > 0:
            path_progress.status = 'in_progress'
        
        path_progress.save()


class UserProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for UserProgress model."""
    
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user).select_related(
            'learning_path', 'module', 'content'
        ).order_by('-last_accessed')


class ConceptViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Concept model."""
    
    queryset = Concept.objects.all()
    serializer_class = ConceptSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by module
        module_id = self.request.query_params.get('module')
        if module_id:
            queryset = queryset.filter(module_id=module_id)
            
        return queryset


class StudentAnswerViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]  # ID-based for now

    def create(self, request):
        """
        POST /learning/answers/
        Save student answer (no evaluation)
        """
        student_id = request.data.get("student_id")
        question_id = request.data.get("question_id")
        response = request.data.get("response")

        if not all([student_id, question_id, response]):
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )

        StudentAnswer.objects.create(
            student_id=student_id,
            question_id=question_id,
            response=response
        )

        return Response(
            {"message": "Answer saved successfully"},
            status=status.HTTP_201_CREATED
        )

class EvaluationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]  # tighten later

    def create(self, request):
        """
        POST /learning/evaluations/
        Teacher triggers AI evaluation
        """
        question_id = request.data.get("question_id")

        if not question_id:
            return Response(
                {"error": "question_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )


        answers = StudentAnswer.objects.filter(question_id=question_id)

        evaluator = AIEvaluator()

        results = []

        for answer in answers:
            ai_result = evaluator.evaluate(
                question=question_id,
                student_answer=answer.response
            )

            evaluation, _ = Evaluation.objects.update_or_create(
                answer=answer,
                defaults={
                    "ai_score": ai_result["score"],
                    "ai_feedback": ai_result["feedback"],
                    "raw_prompt": ai_result["raw_prompt"],
                    "raw_response": ai_result["raw_response"],
                    "evaluated_at": timezone.now()
                }
            )

            results.append({
                "student_id": answer.student_id,
                "ai_score": evaluation.ai_score,
                "ai_feedback": evaluation.ai_feedback
            })

        return Response(results, status=status.HTTP_200_OK)


class FinalScoreViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        """
        POST /learning/finalize/
        Teacher overrides and finalizes score
        """
        student_id = request.data.get("student_id")
        question_id = request.data.get("question_id")
        final_score = request.data.get("final_score")

        if not all([student_id, question_id, final_score]):
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )

        answer = StudentAnswer.objects.get(
            student_id=student_id,
            question_id=question_id
        )

        evaluation, _ = Evaluation.objects.get_or_create(answer=answer)
        evaluation.final_score = final_score
        evaluation.save()

        return Response(
            {"message": "Final score saved"},
            status=status.HTTP_200_OK
        )
