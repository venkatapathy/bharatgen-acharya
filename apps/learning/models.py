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


class Concept(models.Model):
    """Key concepts and mental models."""
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='concepts', null=True, blank=True)
    
    # Relationships
    related_concepts = models.ManyToManyField('self', blank=True, symmetrical=True)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='required_for')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'concepts'
        ordering = ['title']
        
    def __str__(self):
        return self.title


class Content(models.Model):
    """Individual learning content items."""
    
    CONTENT_TYPES = [
        ('text', 'Text/Article'),
        ('video', 'Video'),
        ('mental_model', 'Mental Model'),
        ('code', 'Code Exercise'),
        ('quiz', 'Quiz'),
        ('project', 'Project'),
        ('interactive', 'Interactive Demo'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    order = models.IntegerField(default=0)
    
    # Content Fields
    text_content = models.TextField(blank=True, null=True, help_text="Main textual explanation")
    
    # Video Section
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or video URL")
    video_summary = models.TextField(blank=True, null=True, help_text="Summary of the video content")
    
    # Mental Model Section
    mental_model_title = models.CharField(max_length=200, blank=True, null=True)
    mental_model_description = models.TextField(blank=True, null=True)
    mental_model_image = models.URLField(blank=True, null=True, help_text="URL for mental model diagram")
    
    # Practice/Code Section
    code_content = models.TextField(blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    
    # Quiz/Exercise data
    questions = models.JSONField(default=dict, blank=True, help_text="Quiz questions and answers")
    
    # Slides data
    slides_content = models.JSONField(default=dict, blank=True, help_text="Structured content for slides")
    
    # Generic metadata (kept for flexibility)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional metadata")
    
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

class StudentAnswer(models.Model):
    student_id = models.CharField(max_length=50)
    question_id = models.CharField(max_length=50)
    response = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)


class Evaluation(models.Model):
    answer = models.OneToOneField(StudentAnswer, on_delete=models.CASCADE)

    ai_score = models.FloatField(null=True, blank=True)
    ai_feedback = models.TextField(null=True, blank=True)

    raw_prompt = models.TextField(null=True, blank=True)
    raw_response = models.TextField(null=True, blank=True)

    final_score = models.FloatField(null=True, blank=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Evaluation for {self.answer.student_id} - {self.answer.question_id}"
