from django.contrib import admin
from .models import Recommendation, UserInteraction, SimilarityScore


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation_type', 'item_display', 'score', 'viewed', 'clicked', 'created_at')
    list_filter = ('recommendation_type', 'viewed', 'clicked', 'dismissed', 'created_at')
    search_fields = ('user__username', 'learning_path__title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def item_display(self, obj):
        return obj.learning_path or obj.content
    item_display.short_description = 'Recommended Item'


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'interaction_type', 'item_display', 'duration_seconds', 'rating', 'created_at')
    list_filter = ('interaction_type', 'created_at')
    search_fields = ('user__username', 'learning_path__title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def item_display(self, obj):
        return obj.learning_path or obj.content
    item_display.short_description = 'Content Item'


@admin.register(SimilarityScore)
class SimilarityScoreAdmin(admin.ModelAdmin):
    list_display = ('learning_path_1', 'learning_path_2', 'similarity_score', 'score_type', 'computed_at')
    list_filter = ('score_type', 'computed_at')
    search_fields = ('learning_path_1__title', 'learning_path_2__title')
    readonly_fields = ('computed_at',)

