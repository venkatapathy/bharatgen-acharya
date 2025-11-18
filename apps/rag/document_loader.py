"""
Document loader and chunking utilities for RAG.
"""
import re
from typing import List, Dict, Any
from pathlib import Path
import markdown
from bs4 import BeautifulSoup


class DocumentChunk:
    """Represents a chunk of document with metadata."""
    
    def __init__(self, text: str, metadata: Dict[str, Any]):
        self.text = text
        self.metadata = metadata
    
    def __repr__(self):
        return f"DocumentChunk(text={self.text[:50]}..., metadata={self.metadata})"


class DocumentLoader:
    """Load and process learning materials for RAG."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document loader.
        
        Args:
            chunk_size: Target size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_markdown(self, file_path: str) -> List[DocumentChunk]:
        """
        Load and chunk a markdown file.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            List of document chunks
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert markdown to HTML to better understand structure
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract text while preserving some structure
        text = soup.get_text(separator='\n')
        
        # Metadata
        metadata = {
            'source': file_path,
            'type': 'markdown',
            'filename': Path(file_path).name
        }
        
        return self._chunk_text(text, metadata)
    
    def load_text(self, file_path: str) -> List[DocumentChunk]:
        """
        Load and chunk a plain text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            List of document chunks
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {
            'source': file_path,
            'type': 'text',
            'filename': Path(file_path).name
        }
        
        return self._chunk_text(content, metadata)
    
    def load_content_from_string(
        self,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> List[DocumentChunk]:
        """
        Load and chunk content from a string.
        
        Args:
            content: Text content
            metadata: Optional metadata
            
        Returns:
            List of document chunks
        """
        if metadata is None:
            metadata = {'type': 'string'}
        
        return self._chunk_text(content, metadata)
    
    def _chunk_text(self, text: str, base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Chunk text intelligently, respecting code blocks and paragraphs.
        
        Args:
            text: Text to chunk
            base_metadata: Base metadata for chunks
            
        Returns:
            List of document chunks
        """
        chunks = []
        
        # Split by code blocks first
        code_block_pattern = r'```[\s\S]*?```'
        parts = re.split(code_block_pattern, text)
        code_blocks = re.findall(code_block_pattern, text)
        
        # Interleave text and code blocks
        all_parts = []
        for i, part in enumerate(parts):
            if part.strip():
                all_parts.append(('text', part))
            if i < len(code_blocks):
                all_parts.append(('code', code_blocks[i]))
        
        # Process each part
        for part_type, content in all_parts:
            if part_type == 'code':
                # Keep code blocks intact if possible
                if len(content) <= self.chunk_size:
                    metadata = {**base_metadata, 'content_type': 'code'}
                    chunks.append(DocumentChunk(content, metadata))
                else:
                    # Split large code blocks by lines
                    lines = content.split('\n')
                    current_chunk = []
                    current_size = 0
                    
                    for line in lines:
                        line_size = len(line) + 1
                        if current_size + line_size > self.chunk_size and current_chunk:
                            metadata = {**base_metadata, 'content_type': 'code'}
                            chunks.append(DocumentChunk('\n'.join(current_chunk), metadata))
                            current_chunk = []
                            current_size = 0
                        current_chunk.append(line)
                        current_size += line_size
                    
                    if current_chunk:
                        metadata = {**base_metadata, 'content_type': 'code'}
                        chunks.append(DocumentChunk('\n'.join(current_chunk), metadata))
            
            else:  # text
                # Split by paragraphs
                paragraphs = content.split('\n\n')
                current_chunk = []
                current_size = 0
                
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    
                    para_size = len(para)
                    
                    if current_size + para_size > self.chunk_size and current_chunk:
                        # Save current chunk
                        chunk_text = '\n\n'.join(current_chunk)
                        metadata = {**base_metadata, 'content_type': 'text'}
                        chunks.append(DocumentChunk(chunk_text, metadata))
                        
                        # Start new chunk with overlap
                        if self.chunk_overlap > 0 and current_chunk:
                            overlap_text = current_chunk[-1]
                            current_chunk = [overlap_text]
                            current_size = len(overlap_text)
                        else:
                            current_chunk = []
                            current_size = 0
                    
                    current_chunk.append(para)
                    current_size += para_size + 2  # +2 for \n\n
                
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    metadata = {**base_metadata, 'content_type': 'text'}
                    chunks.append(DocumentChunk(chunk_text, metadata))
        
        # Add chunk indices
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_index'] = i
            chunk.metadata['total_chunks'] = len(chunks)
        
        return chunks
    
    def load_directory(self, directory_path: str, extensions: List[str] = None) -> List[DocumentChunk]:
        """
        Load all documents from a directory.
        
        Args:
            directory_path: Path to directory
            extensions: List of file extensions to include (e.g., ['.md', '.txt'])
            
        Returns:
            List of document chunks from all files
        """
        if extensions is None:
            extensions = ['.md', '.txt']
        
        directory = Path(directory_path)
        chunks = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                try:
                    if file_path.suffix == '.md':
                        file_chunks = self.load_markdown(str(file_path))
                    else:
                        file_chunks = self.load_text(str(file_path))
                    chunks.extend(file_chunks)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return chunks

