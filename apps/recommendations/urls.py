from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendationViewSet, UserInteractionViewSet

router = DefaultRouter()
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'interactions', UserInteractionViewSet, basename='userinteraction')

urlpatterns = [
    path('', include(router.urls)),
]

