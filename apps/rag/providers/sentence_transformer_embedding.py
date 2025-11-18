"""
Sentence Transformer embedding provider.
"""
from typing import List
from sentence_transformers import SentenceTransformer
from ..interfaces import BaseEmbedding


class SentenceTransformerEmbedding(BaseEmbedding):
    """Sentence Transformer embedding provider."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize Sentence Transformer.
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=len(texts) > 10)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension

