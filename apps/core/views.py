from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import UserProfile, UserActivity
from .serializers import (
    UserSerializer, UserProfileSerializer, UserRegistrationSerializer,
    UserUpdateSerializer, UserActivitySerializer
)
from .analytics import UserAnalytics


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profile management."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return self.request.user.profile
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        profile = request.user.profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile."""
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(user).data
        })
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics."""
        analytics = UserAnalytics(request.user)
        stats = analytics.get_dashboard_stats()
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get detailed analytics."""
        days = int(request.query_params.get('days', 30))
        analytics = UserAnalytics(request.user)
        
        return Response({
            'learning_stats': analytics.get_learning_stats(),
            'progress_overview': analytics.get_progress_overview(),
            'time_stats': analytics.get_time_stats(days=days),
            'achievements': analytics.get_achievements()
        })
    
    @action(detail=False, methods=['post'])
    def track_activity(self, request):
        """Track user activity."""
        serializer = UserActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity = serializer.save(user=request.user)
        
        # Update streak
        analytics = UserAnalytics(request.user)
        analytics.update_streak()
        
        return Response({
            'message': 'Activity tracked',
            'activity': UserActivitySerializer(activity).data
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login view (returns JWT tokens)."""
    from django.contrib.auth import authenticate
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout view (blacklist refresh token)."""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Successfully logged out'})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """Get current user information."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

