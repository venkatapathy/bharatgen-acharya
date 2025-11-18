"""
ChromaDB vector store provider.
"""
# Fix for SQLite version issue - use pysqlite3 if available
import sys
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import chromadb
from typing import List, Dict, Any, Optional
import uuid
from ..interfaces import BaseVectorStore


class ChromaDBStore(BaseVectorStore):
    """ChromaDB vector store provider."""
    
    def __init__(self, persist_directory: str, collection_name: str = "learning_content"):
        """
        Initialize ChromaDB store.
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "AI learning content embeddings"}
        )
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents to ChromaDB."""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        # ChromaDB requires all metadata values to be strings, numbers, or booleans
        # Convert lists/dicts to strings
        processed_metadatas = []
        for metadata in metadatas:
            processed = {}
            for key, value in metadata.items():
                if isinstance(value, (list, dict)):
                    processed[key] = str(value)
                else:
                    processed[key] = value
            processed_metadatas.append(processed)
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=processed_metadatas,
            ids=ids
        )
        
        return ids
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents in ChromaDB."""
        where = filter_dict if filter_dict else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i] if results['documents'] else '',
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'score': 1 - results['distances'][0][i] if results['distances'] else 0.0,  # Convert distance to similarity
                })
        
        return formatted_results
    
    def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents by IDs."""
        try:
            self.collection.delete(ids=ids)
            return True
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False
    
    def clear_collection(self) -> bool:
        """Clear all documents from collection."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "AI learning content embeddings"}
            )
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            'name': self.collection_name,
            'count': self.collection.count(),
            'persist_directory': self.persist_directory
        }

