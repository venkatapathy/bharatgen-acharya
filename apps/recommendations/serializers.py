from rest_framework import serializers
from .models import Recommendation, UserInteraction
from apps.learning.serializers import LearningPathListSerializer, ContentSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer for Recommendation model."""
    
    learning_path_detail = LearningPathListSerializer(source='learning_path', read_only=True)
    content_detail = ContentSerializer(source='content', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = [
            'id', 'recommendation_type', 'learning_path', 'learning_path_detail',
            'content', 'content_detail', 'score', 'reasoning', 'viewed',
            'clicked', 'dismissed', 'created_at'
        ]
        read_only_fields = ['created_at']


class UserInteractionSerializer(serializers.ModelSerializer):
    """Serializer for UserInteraction model."""
    
    learning_path_title = serializers.CharField(source='learning_path.title', read_only=True)
    content_title = serializers.CharField(source='content.title', read_only=True)
    
    class Meta:
        model = UserInteraction
        fields = [
            'id', 'interaction_type', 'learning_path', 'learning_path_title',
            'content', 'content_title', 'duration_seconds',
            'completion_percentage', 'rating', 'session_id', 'created_at'
        ]
        read_only_fields = ['created_at']

