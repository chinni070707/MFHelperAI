"""
AI Service - Core AI/ML functionality
"""
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

from app.config_ai import ai_settings

logger = logging.getLogger(__name__)


class AIService:
    """Core AI Service for MFHelper"""
    
    def __init__(self):
        self.enabled = ai_settings.AI_ENABLED and OPENAI_AVAILABLE
        self.client = None
        
        if self.enabled and ai_settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=ai_settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️ AI features disabled - OpenAI API key not configured")
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.enabled and self.client is not None
    
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
