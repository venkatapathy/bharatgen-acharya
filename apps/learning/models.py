from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class LearningPath(models.Model):
    """AI course/learning path container."""
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    estimated_hours = models.IntegerField(help_text="Estimated completion time in hours")
    
    # Metadata
    tags = models.JSONField(default=list, help_text="List of tags for categorization")
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='required_for')
    thumbnail = models.ImageField(upload_to='learning_paths/', blank=True, null=True)
    
    # Statistics
    total_enrollments = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    completion_rate = models.FloatField(default=0.0, help_text="Percentage of users who completed")
    
    # Publishing
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_paths')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_paths'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class Module(models.Model):
    """Sections within a learning path."""
    
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0, help_text="Display order within the learning path")
    
    # Metadata
    estimated_minutes = models.IntegerField(help_text="Estimated completion time in minutes")
    is_optional = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modules'
        ordering = ['learning_path', 'order']
        unique_together = ['learning_path', 'order']
        
    def __str__(self):
        return f"{self.learning_path.title} - {self.title}"


class Content(models.Model):
    """Individual learning content items."""
    
    CONTENT_TYPES = [
        ('text', 'Text/Article'),
        ('video', 'Video'),
        ('code', 'Code Exercise'),
        ('quiz', 'Quiz'),
        ('project', 'Project'),
        ('interactive', 'Interactive Demo'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    order = models.IntegerField(default=0)
    
    # Content
    text_content = models.TextField(blank=True, null=True)
    code_content = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    
    # Quiz/Exercise data
    questions = models.JSONField(default=dict, blank=True, help_text="Quiz questions and answers")
    
    # Metadata
    estimated_minutes = models.IntegerField(default=5)
    difficulty = models.CharField(max_length=20, choices=LearningPath.DIFFICULTY_LEVELS, default='beginner')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'contents'
        ordering = ['module', 'order']
        unique_together = ['module', 'order']
        
    def __str__(self):
        return f"{self.module.title} - {self.title}"


class UserProgress(models.Model):
    """Track user progress through learning content."""
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='user_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='user_progress', null=True, blank=True)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='user_progress', null=True, blank=True)
    
    # Progress tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    time_spent_minutes = models.IntegerField(default=0)
    
    # Assessment
    score = models.FloatField(null=True, blank=True, help_text="Score for quizzes/exercises")
    attempts = models.IntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_progress'
        unique_together = ['user', 'learning_path', 'module', 'content']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['learning_path', 'user']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.learning_path.title} - {self.status}"


class UserEnrollment(models.Model):
    """Track user enrollments in learning paths."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_enrollments'
        unique_together = ['user', 'learning_path']
        
    def __str__(self):
        return f"{self.user.username} enrolled in {self.learning_path.title}"

