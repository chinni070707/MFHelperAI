"""
AI Service - Core AI/ML functionality
Supports both OpenAI (GPT-4) and Local Ollama (TinyLlama)
"""
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
import json
import os

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from app.config_ai import ai_settings

logger = logging.getLogger(__name__)


class AIService:
    """Core AI Service - Supports OpenAI and Ollama"""
    
    def __init__(self):
        self.enabled = ai_settings.AI_ENABLED
        self.client = None
        self.ai_type = os.getenv("AI_TYPE", "openai").lower()  # 'openai' or 'ollama'
        
        if self.ai_type == "ollama":
            self._init_ollama()
        else:
            self._init_openai()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        if self.enabled and OPENAI_AVAILABLE and ai_settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=ai_settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized (GPT-4)")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️ OpenAI not available - check API key")
    
    def _init_ollama(self):
        """Initialize Ollama client"""
        if not REQUESTS_AVAILABLE:
            logger.warning("⚠️ Requests library not available for Ollama")
            return
        
        try:
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            response = requests.get(f"{ollama_url}/api/tags", timeout=2)
            
            if response.status_code == 200:
                self.client = ollama_url
                self.ollama_model = os.getenv("OLLAMA_MODEL", "tinyllama")
                logger.info(f"✅ Ollama available at {ollama_url} with model {self.ollama_model}")
            else:
                logger.warning(f"⚠️ Ollama not responding at {ollama_url}")
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        if self.ai_type == "ollama":
            return self.enabled and self.client is not None
        else:
            return self.enabled and self.client is not None and OPENAI_AVAILABLE
    
    async def generate_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False
    ) -> Optional[str]:
        """Generate completion using GPT"""
        if not self.is_available():
            logger.warning("AI service not available")
            return None
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            kwargs = {
                "model": ai_settings.OPENAI_MODEL,
                "messages": messages,
                "max_tokens": max_tokens or ai_settings.MAX_TOKENS,
                "temperature": temperature or ai_settings.TEMPERATURE,
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**kwargs)
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return None
    
    async def generate_embeddings(self, text: str) -> Optional[List[float]]:
        """Generate embeddings for text"""
        if not self.is_available():
            return None
        
        try:
            response = self.client.embeddings.create(
                model=ai_settings.OPENAI_EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None


# Global AI service instance
ai_service = AIService()
