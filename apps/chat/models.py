from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    """User chat sessions with the AI."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, default="New Chat")
    
    # Context
    learning_path = models.ForeignKey(
        'learning.LearningPath', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Optional learning path context"
    )
    module = models.ForeignKey(
        'learning.Module',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional module context"
    )
    
    # Session metadata
    metadata = models.JSONField(default=dict, help_text="Additional session context and settings")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatMessage(models.Model):
    """Individual messages in a chat session."""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # RAG metadata
    retrieved_contexts = models.JSONField(
        default=list,
        help_text="Retrieved content IDs and snippets used for this response"
    )
    sources = models.JSONField(
        default=list,
        help_text="Source references for the response"
    )
    
    # Generation metadata
    model_used = models.CharField(max_length=100, blank=True, null=True)
    tokens_used = models.IntegerField(null=True, blank=True)
    generation_time_ms = models.IntegerField(null=True, blank=True)
    
    # Feedback
    rating = models.IntegerField(null=True, blank=True, help_text="User rating: 1-5")
    feedback = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
        
    def __str__(self):
        return f"{self.role} - {self.content[:50]}"

