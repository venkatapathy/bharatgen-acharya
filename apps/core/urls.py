from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView, UserProfileViewSet,
    login_view, logout_view, current_user_view
)

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', current_user_view, name='current-user'),
    
    # Profile and analytics
    path('', include(router.urls)),
]

