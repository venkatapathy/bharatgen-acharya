from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer,
    ChatMessageSerializer, SendMessageSerializer
)
from .services import ChatService


class ChatSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for ChatSession model."""
    
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).prefetch_related('messages')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionSerializer
    
    def perform_create(self, serializer):
        """Create a new chat session."""
        chat_service = ChatService()
        session = chat_service.create_session(
            user=self.request.user,
            title=serializer.validated_data.get('title', 'New Chat'),
            learning_path_id=serializer.validated_data.get('learning_path_id'),
            module_id=serializer.validated_data.get('module_id')
        )
        return session
    
    def create(self, request, *args, **kwargs):
        """Override create to use ChatService."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = self.perform_create(serializer)
        
        output_serializer = ChatSessionSerializer(session, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in this session."""
        session = self.get_object()
        
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        chat_service = ChatService()
        
        try:
            assistant_message = chat_service.send_message(
                session=session,
                message=serializer.validated_data['message'],
                use_rag=serializer.validated_data.get('use_rag', True),
                top_k=serializer.validated_data.get('top_k', 5)
            )
            
            return Response({
                'message': ChatMessageSerializer(assistant_message).data,
                'session': ChatSessionSerializer(session, context={'request': request}).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error generating response: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in this session."""
        session = self.get_object()
        messages = session.messages.all().order_by('created_at')
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for this session."""
        session = self.get_object()
        chat_service = ChatService()
        stats = chat_service.get_session_stats(session)
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """Clear all messages in this session."""
        session = self.get_object()
        session.messages.all().delete()
        
        # Add system message
        ChatMessage.objects.create(
            session=session,
            role='system',
            content='Chat cleared. How can I help you?'
        )
        
        return Response({'message': 'Chat cleared successfully'})


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ChatMessage model."""
    
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatMessage.objects.filter(
            session__user=self.request.user
        ).select_related('session')
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate a message."""
        message = self.get_object()
        
        if message.role != 'assistant':
            return Response(
                {'error': 'Can only rate assistant messages'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return Response(
                {'error': 'Rating must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chat_service = ChatService()
        updated_message = chat_service.rate_message(message, int(rating), feedback)
        
        return Response({
            'message': 'Rating saved',
            'data': ChatMessageSerializer(updated_message).data
        })

