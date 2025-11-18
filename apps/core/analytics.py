"""
User analytics and progress tracking.
"""
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.learning.models import UserProgress, UserEnrollment
from .models import UserActivity


class UserAnalytics:
    """Analytics for user progress and engagement."""
    
    def __init__(self, user: User):
        self.user = user
    
    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics."""
        return {
            'learning_stats': self.get_learning_stats(),
            'progress_overview': self.get_progress_overview(),
            'recent_activity': self.get_recent_activity(),
            'achievements': self.get_achievements(),
            'time_stats': self.get_time_stats()
        }
    
    def get_learning_stats(self):
        """Get overall learning statistics."""
        profile = self.user.profile
        
        total_paths = UserEnrollment.objects.filter(
            user=self.user,
            is_active=True
        ).count()
        
        completed_paths = UserProgress.objects.filter(
            user=self.user,
            learning_path__isnull=False,
            module__isnull=True,
            content__isnull=True,
            status='completed'
        ).count()
        
        in_progress_paths = UserProgress.objects.filter(
            user=self.user,
            learning_path__isnull=False,
            module__isnull=True,
            content__isnull=True,
            status='in_progress'
        ).count()
        
        return {
            'enrolled_paths': total_paths,
            'completed_paths': completed_paths,
            'in_progress_paths': in_progress_paths,
            'current_streak': profile.current_streak,
            'longest_streak': profile.longest_streak,
            'total_time_spent': profile.total_time_spent,
            'learning_level': profile.learning_level
        }
    
    def get_progress_overview(self):
        """Get detailed progress overview."""
        progress_data = UserProgress.objects.filter(
            user=self.user,
            learning_path__isnull=False,
            module__isnull=True,
            content__isnull=True
        ).select_related('learning_path')
        
        paths = []
        for progress in progress_data:
            paths.append({
                'id': progress.learning_path.id,
                'title': progress.learning_path.title,
                'status': progress.status,
                'progress_percentage': progress.progress_percentage,
                'time_spent_minutes': progress.time_spent_minutes,
                'last_accessed': progress.last_accessed,
                'estimated_hours': progress.learning_path.estimated_hours
            })
        
        return {
            'paths': paths,
            'average_progress': sum(p['progress_percentage'] for p in paths) / max(len(paths), 1)
        }
    
    def get_recent_activity(self, days: int = 7):
        """Get recent activity."""
        since = timezone.now() - timedelta(days=days)
        
        activities = UserActivity.objects.filter(
            user=self.user,
            timestamp__gte=since
        ).order_by('-timestamp')[:20]
        
        activity_by_day = {}
        for activity in activities:
            day = activity.timestamp.date()
            if day not in activity_by_day:
                activity_by_day[day] = []
            activity_by_day[day].append({
                'type': activity.activity_type,
                'content_type': activity.content_type,
                'timestamp': activity.timestamp
            })
        
        return {
            'recent_activities': [
                {
                    'type': a.activity_type,
                    'content_type': a.content_type,
                    'timestamp': a.timestamp
                }
                for a in activities[:10]
            ],
            'activity_by_day': activity_by_day,
            'total_activities': activities.count()
        }
    
    def get_achievements(self):
        """Get user achievements and milestones."""
        profile = self.user.profile
        achievements = []
        
        # Streak achievements
        if profile.current_streak >= 7:
            achievements.append({
                'title': '7-Day Streak',
                'description': 'Learned for 7 consecutive days',
                'icon': '🔥'
            })
        if profile.current_streak >= 30:
            achievements.append({
                'title': '30-Day Streak',
                'description': 'Learned for 30 consecutive days',
                'icon': '⭐'
            })
        
        # Learning path achievements
        completed = UserProgress.objects.filter(
            user=self.user,
            learning_path__isnull=False,
            module__isnull=True,
            content__isnull=True,
            status='completed'
        ).count()
        
        if completed >= 1:
            achievements.append({
                'title': 'First Path Complete',
                'description': 'Completed your first learning path',
                'icon': '🎓'
            })
        if completed >= 5:
            achievements.append({
                'title': 'Learning Expert',
                'description': 'Completed 5 learning paths',
                'icon': '🏆'
            })
        
        # Time achievements
        if profile.total_time_spent >= 600:  # 10 hours
            achievements.append({
                'title': '10 Hours Learned',
                'description': 'Spent 10 hours learning',
                'icon': '⏰'
            })
        if profile.total_time_spent >= 6000:  # 100 hours
            achievements.append({
                'title': '100 Hours Learned',
                'description': 'Spent 100 hours learning',
                'icon': '🌟'
            })
        
        return achievements
    
    def get_time_stats(self, days: int = 30):
        """Get time-based statistics."""
        since = timezone.now() - timedelta(days=days)
        
        daily_time = UserActivity.objects.filter(
            user=self.user,
            timestamp__gte=since,
            duration_seconds__isnull=False
        ).values('timestamp__date').annotate(
            total_seconds=Sum('duration_seconds')
        ).order_by('timestamp__date')
        
        time_by_day = {
            item['timestamp__date']: item['total_seconds'] // 60
            for item in daily_time
        }
        
        return {
            'time_by_day': time_by_day,
            'total_minutes_period': sum(time_by_day.values()),
            'average_minutes_per_day': sum(time_by_day.values()) / max(len(time_by_day), 1)
        }
    
    def update_streak(self):
        """Update user's learning streak."""
        profile = self.user.profile
        today = timezone.now().date()
        
        # Check if user was active today
        today_activity = UserActivity.objects.filter(
            user=self.user,
            timestamp__date=today
        ).exists()
        
        if not today_activity:
            return
        
        last_activity_date = profile.last_activity_date
        
        if last_activity_date is None:
            # First activity
            profile.current_streak = 1
            profile.longest_streak = 1
        elif last_activity_date == today:
            # Already counted today
            pass
        elif last_activity_date == today - timedelta(days=1):
            # Consecutive day
            profile.current_streak += 1
            if profile.current_streak > profile.longest_streak:
                profile.longest_streak = profile.current_streak
        else:
            # Streak broken
            profile.current_streak = 1
        
        profile.last_activity_date = today
        profile.save()

