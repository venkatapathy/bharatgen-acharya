from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('learning-paths/', TemplateView.as_view(template_name='learning_paths.html'), name='learning-paths'),
    path('learning-paths/<slug:slug>/', TemplateView.as_view(template_name='learning_path_detail.html'), name='learning-path-detail'),
    path('module/<int:id>/', TemplateView.as_view(template_name='module_detail.html'), name='module-detail'),
    path('chat/', TemplateView.as_view(template_name='chat.html'), name='chat'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='frontend-login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='frontend-register'),
]

