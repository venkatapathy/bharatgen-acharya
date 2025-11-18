from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with learning preferences."""
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    interests = models.JSONField(default=list, help_text="List of AI topics of interest")
    learning_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    preferred_learning_style = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Learning statistics
    total_time_spent = models.IntegerField(default=0, help_text="Total learning time in minutes")
    current_streak = models.IntegerField(default=0, help_text="Current learning streak in days")
    longest_streak = models.IntegerField(default=0, help_text="Longest learning streak in days")
    last_activity_date = models.DateField(null=True, blank=True)
    
    # Preferences
    daily_goal_minutes = models.IntegerField(default=30)
    email_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        
    def __str__(self):
        return f"{self.user.username}'s Profile"


class UserActivity(models.Model):
    """Track user interactions for personalization."""
    
    ACTIVITY_TYPES = [
        ('view', 'View Content'),
        ('complete', 'Complete Content'),
        ('like', 'Like Content'),
        ('bookmark', 'Bookmark Content'),
        ('chat', 'Chat Interaction'),
        ('search', 'Search Query'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    content_type = models.CharField(max_length=100, help_text="Type of content interacted with")
    content_id = models.IntegerField(help_text="ID of the content")
    metadata = models.JSONField(default=dict, help_text="Additional activity metadata")
    duration_seconds = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()

