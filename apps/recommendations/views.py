from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Recommendation, UserInteraction
from .serializers import RecommendationSerializer, UserInteractionSerializer
from .engine import get_recommendation_engine


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Recommendation model."""
    
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Recommendation.objects.filter(
            user=self.request.user,
            dismissed=False
        ).select_related('learning_path', 'content')
    
    def list(self, request, *args, **kwargs):
        """Get fresh recommendations for the user."""
        recommendation_type = request.query_params.get('type')
        limit = int(request.query_params.get('limit', 10))
        
        engine = get_recommendation_engine()
        recommendations = engine.get_recommendations(
            user=request.user,
            recommendation_type=recommendation_type,
            limit=limit
        )
        
        # Save recommendations to database
        saved_recommendations = []
        for rec in recommendations:
            # Check if similar recommendation already exists
            existing = Recommendation.objects.filter(
                user=request.user,
                recommendation_type=rec.recommendation_type,
                learning_path=rec.learning_path,
                content=rec.content,
                dismissed=False
            ).first()
            
            if existing:
                saved_recommendations.append(existing)
            else:
                rec.save()
                saved_recommendations.append(rec)
        
        serializer = self.get_serializer(saved_recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark recommendation as viewed."""
        recommendation = self.get_object()
        recommendation.viewed = True
        recommendation.save()
        return Response({'message': 'Marked as viewed'})
    
    @action(detail=True, methods=['post'])
    def mark_clicked(self, request, pk=None):
        """Mark recommendation as clicked."""
        recommendation = self.get_object()
        recommendation.clicked = True
        recommendation.viewed = True
        recommendation.save()
        
        # Track interaction
        engine = get_recommendation_engine()
        engine.track_interaction(
            user=request.user,
            interaction_type='view',
            learning_path=recommendation.learning_path,
            content=recommendation.content,
            referrer='recommendation'
        )
        
        return Response({'message': 'Marked as clicked'})
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a recommendation."""
        recommendation = self.get_object()
        recommendation.dismissed = True
        recommendation.save()
        return Response({'message': 'Recommendation dismissed'})
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Refresh recommendations (clear old and generate new)."""
        # Clear old undismissed recommendations
        Recommendation.objects.filter(
            user=request.user,
            dismissed=False,
            clicked=False
        ).update(dismissed=True)
        
        # Generate new recommendations
        return self.list(request)


class UserInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for UserInteraction model."""
    
    serializer_class = UserInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserInteraction.objects.filter(
            user=self.request.user
        ).select_related('learning_path', 'content').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create interaction."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user interaction statistics."""
        interactions = self.get_queryset()
        
        stats = {
            'total_interactions': interactions.count(),
            'by_type': {},
            'total_time_seconds': sum(i.duration_seconds or 0 for i in interactions),
            'average_rating': sum(i.rating or 0 for i in interactions if i.rating) / max(
                interactions.filter(rating__isnull=False).count(), 1
            )
        }
        
        # Count by type
        for interaction in interactions:
            type_name = interaction.interaction_type
            stats['by_type'][type_name] = stats['by_type'].get(type_name, 0) + 1
        
        return Response(stats)

