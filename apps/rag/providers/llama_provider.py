"""
Llama LLM provider using Ollama.
"""
import ollama
import time
from typing import Dict, Any, Optional
from ..interfaces import BaseLLM


class LlamaProvider(BaseLLM):
    """Llama language model provider via Ollama."""
    
    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """
        Initialize Llama provider.
        
        Args:
            model: Ollama model name
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Ollama."""
        try:
            start_time = time.time()
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            options = {
                "temperature": temperature,
            }
            if max_tokens:
                options["num_predict"] = max_tokens
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options=options,
                **kwargs
            )
            
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "text": response['message']['content'],
                "model": self.model,
                "tokens_used": response.get('eval_count', 0),
                "generation_time_ms": generation_time_ms,
                "finish_reason": "stop",
            }
            
        except Exception as e:
            return {
                "text": f"Error generating response: {str(e)}",
                "model": self.model,
                "tokens_used": 0,
                "generation_time_ms": 0,
                "finish_reason": "error",
                "error": str(e)
            }
    
    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Stream text generation using Ollama."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            options = {
                "temperature": temperature,
            }
            if max_tokens:
                options["num_predict"] = max_tokens
            
            stream = self.client.chat(
                model=self.model,
                messages=messages,
                options=options,
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            yield f"Error: {str(e)}"

