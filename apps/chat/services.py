"""
Chat service for handling RAG-powered conversations.
"""
from typing import Dict, Any, List, Optional
from apps.rag.pipeline import get_rag_pipeline
from .models import ChatSession, ChatMessage


class ChatService:
    """Service for handling chat interactions with RAG."""
    
    def __init__(self):
        self.rag_pipeline = get_rag_pipeline()
    
    def create_session(
        self,
        user,
        title: str = "New Chat",
        learning_path_id: Optional[int] = None,
        module_id: Optional[int] = None
    ) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            user: Django user
            title: Session title
            learning_path_id: Optional learning path context
            module_id: Optional module context
            
        Returns:
            ChatSession instance
        """
        session = ChatSession.objects.create(
            user=user,
            title=title,
            learning_path_id=learning_path_id,
            module_id=module_id
        )
        
        # Add system message
        ChatMessage.objects.create(
            session=session,
            role='system',
            content='Hello! I\'m your AI learning assistant. I can help you with questions about AI and machine learning concepts. How can I help you today?'
        )
        
        return session
    
    def send_message(
        self,
        session: ChatSession,
        message: str,
        use_rag: bool = True,
        top_k: int = 5
    ) -> ChatMessage:
        """
        Send a message and get AI response.
        
        Args:
            session: Chat session
            message: User message
            use_rag: Whether to use RAG for context
            top_k: Number of documents to retrieve
            
        Returns:
            Assistant's ChatMessage
        """
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=message
        )
        
        # Get conversation history
        history = self._get_conversation_history(session)
        
        # Prepare filter for RAG
        filter_dict = None
        if session.learning_path_id:
            filter_dict = {'learning_path_id': session.learning_path_id}
        if session.module_id:
            filter_dict = filter_dict or {}
            filter_dict['module_id'] = session.module_id
        
        # Generate response
        if use_rag:
            response = self.rag_pipeline.query(
                query=message,
                top_k=top_k,
                conversation_history=history,
                filter_dict=filter_dict
            )
        else:
            # Generate without RAG context
            response = self.rag_pipeline.llm.generate(
                prompt=message,
                system_prompt="You are a helpful AI learning assistant."
            )
            response['sources'] = []
            response['context_documents'] = []
        
        # Save assistant message
        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=response.get('text', ''),
            retrieved_contexts=[
                {
                    'text': doc['text'][:500],  # Truncate for storage
                    'score': doc.get('score', 0.0),
                    'metadata': doc.get('metadata', {})
                }
                for doc in response.get('context_documents', [])
            ],
            sources=response.get('sources', []),
            model_used=response.get('model', 'unknown'),
            tokens_used=response.get('tokens_used', 0),
            generation_time_ms=response.get('generation_time_ms', 0)
        )
        
        # Update session title if it's the first user message
        if session.messages.filter(role='user').count() == 1:
            session.title = self._generate_title(message)
            session.save()
        
        return assistant_message
    
    def _get_conversation_history(self, session: ChatSession, last_n: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation history for context.
        
        Args:
            session: Chat session
            last_n: Number of recent messages to include
            
        Returns:
            List of message dicts
        """
        messages = session.messages.filter(role__in=['user', 'assistant']).order_by('-created_at')[:last_n]
        
        history = []
        for msg in reversed(list(messages)):
            history.append({
                'role': msg.role,
                'content': msg.content
            })
        
        return history
    
    def _generate_title(self, first_message: str, max_length: int = 50) -> str:
        """
        Generate a session title from the first message.
        
        Args:
            first_message: First user message
            max_length: Maximum title length
            
        Returns:
            Generated title
        """
        # Take first sentence or first N characters
        sentences = first_message.split('.')
        title = sentences[0].strip()
        
        if len(title) > max_length:
            title = title[:max_length].rsplit(' ', 1)[0] + '...'
        
        return title or "New Chat"
    
    def rate_message(self, message: ChatMessage, rating: int, feedback: str = None) -> ChatMessage:
        """
        Rate an assistant message.
        
        Args:
            message: ChatMessage to rate
            rating: Rating (1-5)
            feedback: Optional feedback text
            
        Returns:
            Updated ChatMessage
        """
        message.rating = rating
        if feedback:
            message.feedback = feedback
        message.save()
        return message
    
    def get_session_stats(self, session: ChatSession) -> Dict[str, Any]:
        """
        Get statistics for a chat session.
        
        Args:
            session: Chat session
            
        Returns:
            Dict with statistics
        """
        messages = session.messages.filter(role='assistant')
        
        return {
            'total_messages': session.messages.count(),
            'user_messages': session.messages.filter(role='user').count(),
            'assistant_messages': messages.count(),
            'total_tokens': sum(msg.tokens_used or 0 for msg in messages),
            'average_generation_time_ms': sum(msg.generation_time_ms or 0 for msg in messages) / max(messages.count(), 1),
            'average_rating': sum(msg.rating or 0 for msg in messages if msg.rating) / max(messages.filter(rating__isnull=False).count(), 1)
        }

