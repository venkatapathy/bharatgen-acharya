from rest_framework import serializers
from django.contrib.auth.models import User
from .models import LearningPath, Module, Content, UserProgress, UserEnrollment


class ContentSerializer(serializers.ModelSerializer):
    """Serializer for Content model."""
    
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Content
        fields = [
            'id', 'title', 'content_type', 'order', 'text_content',
            'code_content', 'video_url', 'external_url', 'questions',
            'estimated_minutes', 'difficulty', 'user_progress'
        ]
    
    def get_user_progress(self, obj):
        """Get user progress for this content."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(
                    user=request.user,
                    content=obj
                )
                return {
                    'status': progress.status,
                    'progress_percentage': progress.progress_percentage,
                    'time_spent_minutes': progress.time_spent_minutes,
                    'score': progress.score
                }
            except UserProgress.DoesNotExist:
                return None
        return None


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Module model."""
    
    contents = ContentSerializer(many=True, read_only=True)
    content_count = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order', 'estimated_minutes',
            'is_optional', 'contents', 'content_count', 'user_progress'
        ]
    
    def get_content_count(self, obj):
        """Get number of contents in this module."""
        return obj.contents.count()
    
    def get_user_progress(self, obj):
        """Get user progress for this module."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(
                    user=request.user,
                    module=obj
                )
                return {
                    'status': progress.status,
                    'progress_percentage': progress.progress_percentage,
                    'time_spent_minutes': progress.time_spent_minutes
                }
            except UserProgress.DoesNotExist:
                return None
        return None


class ModuleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for module lists."""
    
    content_count = serializers.IntegerField(source='contents.count', read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'estimated_minutes', 'is_optional', 'content_count']


class LearningPathSerializer(serializers.ModelSerializer):
    """Serializer for LearningPath model."""
    
    modules = ModuleSerializer(many=True, read_only=True)
    module_count = serializers.SerializerMethodField()
    user_enrollment = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'title', 'slug', 'description', 'difficulty_level',
            'estimated_hours', 'tags', 'thumbnail', 'total_enrollments',
            'average_rating', 'completion_rate', 'is_published',
            'modules', 'module_count', 'user_enrollment', 'user_progress'
        ]
    
    def get_module_count(self, obj):
        """Get number of modules in this path."""
        return obj.modules.count()
    
    def get_user_enrollment(self, obj):
        """Check if user is enrolled."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserEnrollment.objects.filter(
                user=request.user,
                learning_path=obj,
                is_active=True
            ).exists()
        return False
    
    def get_user_progress(self, obj):
        """Get overall user progress for this path."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(
                    user=request.user,
                    learning_path=obj,
                    module__isnull=True,
                    content__isnull=True
                )
                return {
                    'status': progress.status,
                    'progress_percentage': progress.progress_percentage,
                    'time_spent_minutes': progress.time_spent_minutes,
                    'started_at': progress.started_at,
                    'last_accessed': progress.last_accessed
                }
            except UserProgress.DoesNotExist:
                return None
        return None


class LearningPathListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for learning path lists."""
    
    module_count = serializers.IntegerField(source='modules.count', read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'title', 'slug', 'description', 'difficulty_level',
            'estimated_hours', 'tags', 'thumbnail', 'total_enrollments',
            'average_rating', 'module_count', 'is_enrolled'
        ]
    
    def get_is_enrolled(self, obj):
        """Check if user is enrolled."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserEnrollment.objects.filter(
                user=request.user,
                learning_path=obj,
                is_active=True
            ).exists()
        return False


class UserProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserProgress model."""
    
    learning_path_title = serializers.CharField(source='learning_path.title', read_only=True)
    module_title = serializers.CharField(source='module.title', read_only=True)
    content_title = serializers.CharField(source='content.title', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'learning_path', 'learning_path_title', 'module',
            'module_title', 'content', 'content_title', 'status',
            'progress_percentage', 'time_spent_minutes', 'score',
            'attempts', 'started_at', 'completed_at', 'last_accessed'
        ]
        read_only_fields = ['started_at', 'last_accessed']


class UserEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for UserEnrollment model."""
    
    learning_path_detail = LearningPathListSerializer(source='learning_path', read_only=True)
    
    class Meta:
        model = UserEnrollment
        fields = ['id', 'learning_path', 'learning_path_detail', 'enrolled_at', 'is_active']
        read_only_fields = ['enrolled_at']

