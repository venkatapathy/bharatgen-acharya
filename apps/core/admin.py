from django.contrib import admin
from .models import UserProfile, UserActivity


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'learning_level', 'total_time_spent', 'current_streak', 'created_at')
    list_filter = ('learning_level', 'email_notifications')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'bio', 'avatar')
        }),
        ('Learning Preferences', {
            'fields': ('interests', 'learning_level', 'preferred_learning_style', 'daily_goal_minutes')
        }),
        ('Statistics', {
            'fields': ('total_time_spent', 'current_streak', 'longest_streak', 'last_activity_date')
        }),
        ('Settings', {
            'fields': ('email_notifications',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'content_type', 'content_id', 'timestamp')
    list_filter = ('activity_type', 'content_type', 'timestamp')
    search_fields = ('user__username',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

