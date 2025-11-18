"""
RAG pipeline for orchestrating retrieval and generation.
"""
from typing import List, Dict, Any, Optional
from django.conf import settings
from .interfaces import BaseLLM, BaseEmbedding, BaseVectorStore
from .providers.llama_provider import LlamaProvider
from .providers.sentence_transformer_embedding import SentenceTransformerEmbedding
from .providers.chromadb_store import ChromaDBStore
from .document_loader import DocumentLoader, DocumentChunk


class RAGPipeline:
    """Main RAG pipeline for retrieval and generation."""
    
    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        embedding: Optional[BaseEmbedding] = None,
        vector_store: Optional[BaseVectorStore] = None
    ):
        """
        Initialize RAG pipeline with pluggable components.
        
        Args:
            llm: Language model provider (defaults to LlamaProvider)
            embedding: Embedding provider (defaults to SentenceTransformerEmbedding)
            vector_store: Vector store provider (defaults to ChromaDBStore)
        """
        rag_config = settings.RAG_CONFIG
        
        # Initialize components with defaults
        self.llm = llm or LlamaProvider(
            model=rag_config['LLM_MODEL'],
            base_url=rag_config['OLLAMA_BASE_URL']
        )
        
        self.embedding = embedding or SentenceTransformerEmbedding(
            model_name=rag_config['EMBEDDING_MODEL']
        )
        
        self.vector_store = vector_store or ChromaDBStore(
            persist_directory=rag_config['CHROMA_PERSIST_DIR']
        )
        
        self.document_loader = DocumentLoader()
        self.rag_config = rag_config
    
    def index_documents(
        self,
        chunks: List[DocumentChunk],
        batch_size: int = 32
    ) -> List[str]:
        """
        Index document chunks into the vector store.
        
        Args:
            chunks: List of document chunks
            batch_size: Batch size for embedding
            
        Returns:
            List of document IDs
        """
        all_ids = []
        
        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Extract texts and metadata
            texts = [chunk.text for chunk in batch]
            metadatas = [chunk.metadata for chunk in batch]
            
            # Generate embeddings
            embeddings = self.embedding.embed_texts(texts)
            
            # Add to vector store
            ids = self.vector_store.add_documents(
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            all_ids.extend(ids)
        
        return all_ids
    
    def index_content_from_db(self, learning_path_id: Optional[int] = None):
        """
        Index learning content from database.
        
        Args:
            learning_path_id: Optional ID to index specific learning path
        """
        from apps.learning.models import Content, Module, LearningPath
        
        if learning_path_id:
            contents = Content.objects.filter(
                module__learning_path_id=learning_path_id
            ).select_related('module', 'module__learning_path')
        else:
            contents = Content.objects.all().select_related(
                'module', 'module__learning_path'
            )
        
        chunks = []
        for content in contents:
            # Combine text and code content
            full_text = []
            if content.text_content:
                full_text.append(content.text_content)
            if content.code_content:
                full_text.append(f"```\n{content.code_content}\n```")
            
            if not full_text:
                continue
            
            text = '\n\n'.join(full_text)
            
            # Create metadata
            metadata = {
                'content_id': content.id,
                'content_title': content.title,
                'content_type': content.content_type,
                'module_id': content.module.id,
                'module_title': content.module.title,
                'learning_path_id': content.module.learning_path.id,
                'learning_path_title': content.module.learning_path.title,
                'difficulty': content.difficulty,
                'source': 'database'
            }
            
            # Chunk the content
            content_chunks = self.document_loader.load_content_from_string(
                text, metadata
            )
            chunks.extend(content_chunks)
        
        # Index all chunks
        if chunks:
            return self.index_documents(chunks)
        return []
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            top_k: Number of results (defaults to RAG_CONFIG['TOP_K'])
            filter_dict: Optional metadata filters
            
        Returns:
            List of retrieved documents with scores
        """
        if top_k is None:
            top_k = self.rag_config['TOP_K']
        
        # Generate query embedding
        query_embedding = self.embedding.embed_text(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        return results
    
    def generate_with_context(
        self,
        query: str,
        context_documents: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate response using retrieved context.
        
        Args:
            query: User query
            context_documents: Retrieved documents
            system_prompt: Optional system prompt
            conversation_history: Optional conversation history
            
        Returns:
            Generated response with metadata
        """
        # Build context from retrieved documents
        context_parts = []
        sources = []
        
        for i, doc in enumerate(context_documents, 1):
            context_parts.append(f"[Source {i}]\n{doc['text']}\n")
            sources.append({
                'index': i,
                'metadata': doc.get('metadata', {}),
                'score': doc.get('score', 0.0)
            })
        
        context = "\n".join(context_parts)
        
        # Build prompt
        if system_prompt is None:
            system_prompt = """You are an AI learning assistant specializing in AI and machine learning education. 
Your role is to help users learn about AI concepts, answer questions, and guide them through learning materials.
Use the provided context to answer questions accurately. If the context doesn't contain enough information, 
say so and provide general knowledge while encouraging the user to explore relevant learning materials."""
        
        # Add conversation history if provided
        full_prompt = f"""Context from learning materials:
{context}

User question: {query}

Please provide a helpful, accurate, and educational response based on the context above."""
        
        if conversation_history:
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
            full_prompt = f"Previous conversation:\n{history_text}\n\n{full_prompt}"
        
        # Generate response
        response = self.llm.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=self.rag_config['TEMPERATURE'],
            max_tokens=self.rag_config['MAX_CONTEXT_LENGTH']
        )
        
        # Add sources to response
        response['sources'] = sources
        response['context_documents'] = context_documents
        
        return response
    
    def query(
        self,
        query: str,
        top_k: int = None,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Full RAG query: retrieve and generate.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            system_prompt: Optional system prompt
            conversation_history: Optional conversation history
            filter_dict: Optional metadata filters
            
        Returns:
            Generated response with sources and metadata
        """
        # Retrieve relevant documents
        context_documents = self.retrieve(
            query=query,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        # Generate response with context
        response = self.generate_with_context(
            query=query,
            context_documents=context_documents,
            system_prompt=system_prompt,
            conversation_history=conversation_history
        )
        
        return response
    
    def clear_index(self) -> bool:
        """Clear all indexed documents."""
        return self.vector_store.clear_collection()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        return {
            'vector_store': self.vector_store.get_collection_stats(),
            'embedding_dimension': self.embedding.get_dimension(),
            'llm_model': self.llm.model if hasattr(self.llm, 'model') else 'unknown',
        }


# Singleton instance
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create the RAG pipeline singleton."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline

