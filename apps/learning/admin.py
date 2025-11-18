from django.contrib import admin
from .models import LearningPath, Module, Content, UserProgress, UserEnrollment


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ('title', 'order', 'estimated_minutes', 'is_optional')


class ContentInline(admin.TabularInline):
    model = Content
    extra = 1
    fields = ('title', 'content_type', 'order', 'estimated_minutes')


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty_level', 'estimated_hours', 'is_published', 'total_enrollments', 'created_at')
    list_filter = ('difficulty_level', 'is_published', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('prerequisites',)
    inlines = [ModuleInline]
    readonly_fields = ('created_at', 'updated_at', 'total_enrollments', 'average_rating', 'completion_rate')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'thumbnail')
        }),
        ('Learning Details', {
            'fields': ('difficulty_level', 'estimated_hours', 'tags', 'prerequisites')
        }),
        ('Statistics', {
            'fields': ('total_enrollments', 'average_rating', 'completion_rate'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'learning_path', 'order', 'estimated_minutes', 'is_optional')
    list_filter = ('learning_path', 'is_optional')
    search_fields = ('title', 'description')
    inlines = [ContentInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'content_type', 'order', 'estimated_minutes', 'difficulty')
    list_filter = ('content_type', 'difficulty', 'module__learning_path')
    search_fields = ('title', 'text_content')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'content_type', 'order')
        }),
        ('Content', {
            'fields': ('text_content', 'code_content', 'video_url', 'external_url', 'questions')
        }),
        ('Metadata', {
            'fields': ('estimated_minutes', 'difficulty')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'learning_path', 'status', 'progress_percentage', 'time_spent_minutes', 'last_accessed')
    list_filter = ('status', 'learning_path', 'started_at')
    search_fields = ('user__username', 'learning_path__title')
    readonly_fields = ('started_at', 'last_accessed')
    date_hierarchy = 'last_accessed'


@admin.register(UserEnrollment)
class UserEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'learning_path', 'enrolled_at', 'is_active')
    list_filter = ('is_active', 'enrolled_at')
    search_fields = ('user__username', 'learning_path__title')
    readonly_fields = ('enrolled_at',)
    date_hierarchy = 'enrolled_at'

