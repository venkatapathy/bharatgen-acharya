from django.contrib import admin
from .models import ChatSession, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    fields = ('role', 'content', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'learning_path', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'learning_path')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ChatMessageInline]
    date_hierarchy = 'created_at'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'model_used', 'created_at')
    list_filter = ('role', 'session__user', 'created_at')
    search_fields = ('content', 'session__title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

