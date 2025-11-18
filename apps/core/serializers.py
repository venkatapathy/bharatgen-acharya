from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, UserActivity


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'interests', 'learning_level', 'preferred_learning_style',
            'avatar', 'total_time_spent', 'current_streak', 'longest_streak',
            'last_activity_date', 'daily_goal_minutes', 'email_notifications',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_time_spent', 'current_streak', 'longest_streak',
            'last_activity_date', 'created_at', 'updated_at'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    # Profile fields
    learning_level = serializers.ChoiceField(
        choices=UserProfile.LEVEL_CHOICES,
        default='beginner'
    )
    interests = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'learning_level', 'interests'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        learning_level = validated_data.pop('learning_level', 'beginner')
        interests = validated_data.pop('interests', [])
        validated_data.pop('password2')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        
        # Update profile
        user.profile.learning_level = learning_level
        user.profile.interests = interests
        user.profile.save()
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    learning_level = serializers.ChoiceField(
        choices=UserProfile.LEVEL_CHOICES,
        source='profile.learning_level'
    )
    interests = serializers.ListField(
        child=serializers.CharField(),
        source='profile.interests'
    )
    bio = serializers.CharField(source='profile.bio', allow_blank=True)
    daily_goal_minutes = serializers.IntegerField(source='profile.daily_goal_minutes')
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'learning_level', 'interests', 'bio', 'daily_goal_minutes'
        ]
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile fields
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        return instance


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model."""
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'content_type', 'content_id',
            'metadata', 'duration_seconds', 'timestamp'
        ]
        read_only_fields = ['timestamp']

