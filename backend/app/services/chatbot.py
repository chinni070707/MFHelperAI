"""
AI Chatbot - Natural language portfolio queries
"""
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class PortfolioChatbot:
    """AI-powered chatbot for portfolio queries"""
    
    def __init__(self):
        self.conversation_history = {}  # user_id -> messages
    
    async def chat(
        self,
        user_id: int,
        message: str,
        portfolio_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user message and return AI response
        """
        try:
            if not ai_service.is_available():
                return {
                    "response": "AI chatbot is currently unavailable. Please try again later.",
                    "type": "error"
                }
            
            # Get or create conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Build context from portfolio data
            context = self._build_portfolio_context(portfolio_data) if portfolio_data else ""
            
            # Prepare system message
            system_message = f"""You are an AI financial assistant for MFHelper, helping users understand their mutual fund portfolio.

{context}

Guidelines:
- Be conversational and friendly
- Provide specific numbers from the portfolio when relevant
- Explain financial terms simply
- Give actionable advice
- Keep responses concise (2-3 paragraphs max)
- Use emojis sparingly for engagement
"""
            
            # Generate response
            response_text = await ai_service.generate_completion(
                prompt=message,
                system_message=system_message,
                max_tokens=500,
                temperature=0.8
            )
            
            if not response_text:
                return {
                    "response": "I'm having trouble processing that. Could you rephrase your question?",
                    "type": "error"
                }
            
            # Store conversation
            self.conversation_history[user_id].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Limit history to last 10 messages
            if len(self.conversation_history[user_id]) > 10:
                self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
            
            return {
                "response": response_text,
                "type": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in chatbot: {e}")
            return {
                "response": "I encountered an error. Please try asking differently.",
                "type": "error"
            }
    
    def _build_portfolio_context(self, portfolio_data: Dict[str, Any]) -> str:
        """Build context string from portfolio data"""
        if not portfolio_data:
            return "No portfolio data available."
        
        holdings = portfolio_data.get('holdings', [])
        if not holdings:
            return "Portfolio is empty."
        
        total_value = sum(h.get('current_value', 0) for h in holdings)
        total_invested = sum(h.get('invested_value', 0) for h in holdings)
        total_returns = sum(h.get('returns', 0) for h in holdings)
        return_pct = (total_returns / total_invested * 100) if total_invested > 0 else 0
        
        # Top holdings
        top_holdings = sorted(
            holdings,
            key=lambda x: x.get('current_value', 0),
            reverse=True
        )[:3]
        
        # Category breakdown
        from collections import defaultdict
        category_values = defaultdict(float)
        for h in holdings:
            category_values[h.get('category', 'Unknown')] += h.get('current_value', 0)
        
        context = f"""Current Portfolio Data:
- Total Holdings: {len(holdings)} funds
- Total Value: ₹{total_value:,.2f}
- Invested: ₹{total_invested:,.2f}
- Returns: ₹{total_returns:,.2f} ({return_pct:+.2f}%)

Top 3 Holdings:
{chr(10).join([f"- {h.get('fund_name', 'Unknown')}: ₹{h.get('current_value', 0):,.2f}" for h in top_holdings])}

Category Allocation:
{chr(10).join([f"- {cat}: ₹{val:,.2f} ({val/total_value*100:.1f}%)" for cat, val in sorted(category_values.items(), key=lambda x: x[1], reverse=True)[:5]])}
"""
        return context
    
    def clear_history(self, user_id: int):
        """Clear conversation history for user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]


# Global chatbot instance
chatbot = PortfolioChatbot()
