"""
URL configuration for BharatGen Acharya project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('apps.core.urls')),
    path('api/learning/', include('apps.learning.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
    
    # Frontend views
    path('', include('apps.core.frontend_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

