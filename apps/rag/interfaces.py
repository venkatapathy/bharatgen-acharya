"""
Abstract interfaces for pluggable RAG components.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLM(ABC):
    """Abstract base class for Language Model providers."""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text from the language model.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict with 'text', 'tokens_used', 'model', etc.
        """
        pass
    
    @abstractmethod
    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Stream text generation from the language model.
        
        Yields:
            Chunks of generated text
        """
        pass


class BaseEmbedding(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Integer dimension size
        """
        pass


class BaseVectorStore(ABC):
    """Abstract base class for vector store providers."""
    
    @abstractmethod
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents with their embeddings to the store.
        
        Args:
            texts: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional metadata for each document
            ids: Optional custom IDs for documents
            
        Returns:
            List of document IDs
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_dict: Optional filters for metadata
            
        Returns:
            List of dicts with 'id', 'text', 'metadata', 'score'
        """
        pass
    
    @abstractmethod
    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.
        
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dict with collection statistics
        """
        pass

