from django.db import models
from django.contrib.auth.models import User


class Recommendation(models.Model):
    """Personalized content recommendations."""
    
    RECOMMENDATION_TYPES = [
        ('next_content', 'Next Content'),
        ('similar_path', 'Similar Learning Path'),
        ('collaborative', 'Users Also Learned'),
        ('skill_gap', 'Fill Knowledge Gap'),
        ('trending', 'Trending Content'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    
    # Recommended item
    learning_path = models.ForeignKey(
        'learning.LearningPath',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    content = models.ForeignKey(
        'learning.Content',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Recommendation metadata
    score = models.FloatField(help_text="Recommendation confidence score")
    reasoning = models.TextField(help_text="Why this is recommended")
    metadata = models.JSONField(default=dict, help_text="Additional recommendation data")
    
    # Interaction tracking
    viewed = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When recommendation becomes stale")
    
    class Meta:
        db_table = 'recommendations'
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['recommendation_type', '-score']),
        ]
        
    def __str__(self):
        item = self.learning_path or self.content
        return f"{self.user.username} - {self.recommendation_type} - {item}"


class UserInteraction(models.Model):
    """Track user interactions with content for recommendation engine."""
    
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('complete', 'Complete'),
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('bookmark', 'Bookmark'),
        ('share', 'Share'),
        ('skip', 'Skip'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    
    # Interacted item
    learning_path = models.ForeignKey(
        'learning.LearningPath',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='interactions'
    )
    content = models.ForeignKey(
        'learning.Content',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='interactions'
    )
    
    # Interaction details
    duration_seconds = models.IntegerField(null=True, blank=True)
    completion_percentage = models.FloatField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True, help_text="User rating: 1-5")
    
    # Context
    session_id = models.CharField(max_length=100, blank=True, null=True)
    referrer = models.CharField(max_length=200, blank=True, null=True, help_text="How user found this content")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'interaction_type', '-created_at']),
            models.Index(fields=['learning_path', '-created_at']),
            models.Index(fields=['content', '-created_at']),
        ]
        
    def __str__(self):
        item = self.learning_path or self.content
        return f"{self.user.username} - {self.interaction_type} - {item}"


class SimilarityScore(models.Model):
    """Pre-computed similarity scores between content items."""
    
    learning_path_1 = models.ForeignKey(
        'learning.LearningPath',
        on_delete=models.CASCADE,
        related_name='similarity_as_first'
    )
    learning_path_2 = models.ForeignKey(
        'learning.LearningPath',
        on_delete=models.CASCADE,
        related_name='similarity_as_second'
    )
    
    similarity_score = models.FloatField(help_text="Cosine similarity or other metric")
    score_type = models.CharField(
        max_length=30,
        default='embedding',
        help_text="Type of similarity: embedding, collaborative, content-based"
    )
    
    computed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'similarity_scores'
        unique_together = ['learning_path_1', 'learning_path_2', 'score_type']
        indexes = [
            models.Index(fields=['learning_path_1', '-similarity_score']),
        ]
        
    def __str__(self):
        return f"{self.learning_path_1} <-> {self.learning_path_2}: {self.similarity_score:.3f}"

