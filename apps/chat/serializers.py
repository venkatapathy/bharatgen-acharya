from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model."""
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'role', 'content', 'retrieved_contexts', 'sources',
            'model_used', 'tokens_used', 'generation_time_ms',
            'rating', 'feedback', 'created_at'
        ]
        read_only_fields = [
            'retrieved_contexts', 'sources', 'model_used',
            'tokens_used', 'generation_time_ms', 'created_at'
        ]


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for ChatSession model."""
    
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    learning_path_title = serializers.CharField(source='learning_path.title', read_only=True)
    module_title = serializers.CharField(source='module.title', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'learning_path', 'learning_path_title',
            'module', 'module_title', 'metadata', 'is_active',
            'messages', 'message_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_message_count(self, obj):
        """Get number of messages in session."""
        return obj.messages.count()


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for chat session lists."""
    
    message_count = serializers.IntegerField(source='messages.count', read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'title', 'is_active', 'message_count',
            'last_message', 'created_at', 'updated_at'
        ]
    
    def get_last_message(self, obj):
        """Get preview of last message."""
        last_msg = obj.messages.filter(role='assistant').last()
        if last_msg:
            return {
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'created_at': last_msg.created_at
            }
        return None


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending a message."""
    
    message = serializers.CharField(required=True)
    learning_path_id = serializers.IntegerField(required=False, allow_null=True)
    module_id = serializers.IntegerField(required=False, allow_null=True)
    use_rag = serializers.BooleanField(default=True)
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20)

