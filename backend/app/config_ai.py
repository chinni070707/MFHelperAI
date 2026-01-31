"""
AI Service Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class AISettings(BaseSettings):
    """AI/ML Configuration"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Claude Configuration (alternative)
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = "claude-3-sonnet-20240229"
    
    # AI Feature Flags
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "true").lower() == "true"
    PORTFOLIO_ANALYSIS_ENABLED: bool = True
    CHATBOT_ENABLED: bool = True
    GOAL_PLANNING_ENABLED: bool = True
    RECOMMENDATIONS_ENABLED: bool = True
    ALERTS_ENABLED: bool = True
    
    # AI Parameters
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    TOP_P: float = 1.0
    FREQUENCY_PENALTY: float = 0.0
    PRESENCE_PENALTY: float = 0.0
    
    # Caching
    CACHE_AI_RESPONSES: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    
    # Rate Limiting
    AI_RATE_LIMIT_PER_USER: int = 50  # requests per hour
    AI_RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    
    # Cost Control
    MAX_COST_PER_REQUEST: float = 0.50  # USD
    DAILY_COST_LIMIT: float = 50.0  # USD
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: str = "./data/chromadb"
    CHROMA_COLLECTION: str = "mfhelper_knowledge"
    
    # Scoring Weights
    HEALTH_SCORE_WEIGHTS: dict = {
        "diversification": 0.25,
        "allocation": 0.25,
        "performance": 0.20,
        "risk": 0.15,
        "cost": 0.15
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
ai_settings = AISettings()
