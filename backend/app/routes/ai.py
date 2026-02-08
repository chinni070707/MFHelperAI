"""
AI Routes - API endpoints for AI features
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.database import get_db
from app.models.models import User
from app.utils.auth import get_current_user
from app.services.portfolio_analyzer import portfolio_analyzer
from app.services.chatbot import chatbot
from app.services.goal_planner import goal_planner, GoalType

router = APIRouter(prefix="/ai", tags=["AI"])
logger = logging.getLogger(__name__)


# Request/Response Models
class PortfolioAnalysisResponse(BaseModel):
    health_score: float
    health_grade: str
    scores: Dict[str, float]
    insights: List[Dict[str, str]]
    recommendations: List[str]
    analyzed_at: str
    holdings_count: int
    total_value: float


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)


class ChatResponse(BaseModel):
    response: str
    type: str
    timestamp: str


class GoalPlanRequest(BaseModel):
    goal_name: str = Field(..., min_length=1, max_length=100)
    goal_type: GoalType = GoalType.CUSTOM
    target_amount: float = Field(..., gt=0)
    time_horizon: int = Field(..., ge=1, le=50)
    current_portfolio_value: float = Field(default=0, ge=0)
    monthly_investment: float = Field(default=0, ge=0)
    risk_tolerance: str = Field(default="moderate", pattern="^(low|moderate|high)$")
    user_age: Optional[int] = Field(default=None, ge=18, le=100)


class GoalPlanResponse(BaseModel):
    goal_name: str
    goal_type: str
    target_amount: float
    time_horizon_years: int
    inflation_adjusted_amount: float
    current_value: float
    monthly_investment: float
    required_monthly_sip: float
    projected_value: float
    gap: float
    gap_percentage: float
    on_track: bool
    allocation_strategy: Dict[str, float]
    milestones: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]
    created_at: str


# ===========================================
# PHASE 1: Portfolio Analysis + Chatbot
# ===========================================

@router.get("/portfolio/analyze", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze portfolio health and generate AI insights
    
    Returns:
    - Health score (0-100)
    - Component scores (diversification, allocation, performance, risk, cost)
    - Actionable insights
    - AI-powered recommendations
    """
    try:
        # Get user's portfolio
        from app.models.models import Portfolio, Holding
        
        portfolio = db.query(Portfolio).filter(
            Portfolio.user_id == current_user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found. Please upload your portfolio first."
            )
        
        # Get holdings
        holdings = db.query(Holding).filter(
            Holding.portfolio_id == portfolio.id
        ).all()
        
        if not holdings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio has no holdings"
            )
        
        # Prepare portfolio data
        portfolio_data = {
            "portfolio_id": portfolio.id,
            "holdings": [
                {
                    "fund_name": h.fund_name,
                    "scheme_code": h.scheme_code,
                    "amc": h.amc,
                    "category": h.category,
                    "current_value": float(h.current_value),
                    "invested_value": float(h.invested_value),
                    "returns": float(h.returns),
                    "return_pct": float(h.return_pct),
                    "units": float(h.units)
                }
                for h in holdings
            ]
        }
        
        # Analyze portfolio
        analysis = await portfolio_analyzer.analyze_portfolio(portfolio_data)
        
        logger.info(f"Portfolio analyzed for user {current_user.id}: Health Score {analysis['health_score']}")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze portfolio"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI about portfolio
    
    Ask questions like:
    - "Which fund gave me best returns?"
    - "Should I invest more in debt funds?"
    - "Explain expense ratio"
    - "How is my portfolio performing?"
    """
    try:
        # Get user's portfolio data
        from app.models.models import Portfolio, Holding
        
        portfolio = db.query(Portfolio).filter(
            Portfolio.user_id == current_user.id
        ).first()
        
        portfolio_data = None
        if portfolio:
            holdings = db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id
            ).all()
            
            portfolio_data = {
                "holdings": [
                    {
                        "fund_name": h.fund_name,
                        "amc": h.amc,
                        "category": h.category,
                        "current_value": float(h.current_value),
                        "invested_value": float(h.invested_value),
                        "returns": float(h.returns),
                        "return_pct": float(h.return_pct)
                    }
                    for h in holdings
                ]
            }
        
        # Chat with AI
        response = await chatbot.chat(
            user_id=current_user.id,
            message=request.message,
            portfolio_data=portfolio_data
        )
        
        logger.info(f"Chat request from user {current_user.id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.delete("/chat/history")
async def clear_chat_history(
    current_user: User = Depends(get_current_user)
):
    """Clear chat conversation history"""
    try:
        chatbot.clear_history(current_user.id)
        return {"message": "Chat history cleared"}
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )


# ===========================================
# PHASE 2: Goal Planning
# ===========================================

@router.post("/goals/plan", response_model=GoalPlanResponse)
async def create_goal_plan(
    request: GoalPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create AI-powered goal-based investment plan
    
    Examples:
    - Retirement: ₹5 Cr in 25 years
    - House: ₹50 L in 5 years
    - Education: ₹25 L in 10 years
    
    AI will calculate:
    - Inflation-adjusted target
    - Required monthly SIP
    - Allocation strategy
    - Milestones
    - Personalized recommendations
    """
    try:
        plan = await goal_planner.create_goal_plan(
            goal_name=request.goal_name,
            goal_type=request.goal_type,
            target_amount=request.target_amount,
            time_horizon=request.time_horizon,
            current_portfolio_value=request.current_portfolio_value,
            monthly_investment=request.monthly_investment,
            risk_tolerance=request.risk_tolerance,
            user_age=request.user_age
        )
        
        if "error" in plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=plan["message"]
            )
        
        logger.info(f"Goal plan created for user {current_user.id}: {request.goal_name}")
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating goal plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create goal plan"
        )


@router.get("/status")
async def ai_status():
    """Check AI service status"""
    # AI service removed - using non-AI strategy
    # from app.services.ai_service import ai_service
    
    return {
        "ai_available": False,
        "features": {
            "portfolio_analysis": True,
            "chatbot": False,
            "goal_planning": True,
            "recommendations": False,
        }
    }


@router.get("/health")
async def ai_health():
    """AI health endpoint for frontend checks

    Returns JSON with availability, provider (ollama/openai), model (if available), and message.
    """
    # AI service removed - using non-AI strategy
    # from app.services.ai_service import ai_service

    available = False
    provider = "none"
    model = None
    message = "AI available"

    if provider == "ollama":
        model = None  # AI service removed
        if not available:
            message = "Ollama/TinyLlama not available - AI offline"
    elif provider == "openai":
        model = None  # AI service removed
        if not available:
            message = "OpenAI not available or API key missing"
    else:
        message = "AI provider not configured"

    return {
        "available": available,
        "provider": provider,
        "model": model,
        "message": message
    }
