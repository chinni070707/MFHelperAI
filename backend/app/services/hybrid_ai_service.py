"""
Hybrid AI Service - Combines Rule-Based + TinyLlama AI
Optimal for portfolio analysis (80% rule-based) + general chat (20% AI)
"""
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging
import re

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class HybridAIService:
    """
    Hybrid AI Service combining:
    - Rule-based system for portfolio analysis (INSTANT ⚡)
    - TinyLlama via Ollama for general questions (1-2 sec)
    """
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434", ollama_model: str = "tinyllama"):
        self.ollama_base_url = ollama_base_url
        self.ollama_model = ollama_model
        self.ollama_available = self._check_ollama()
        
        if self.ollama_available:
            logger.info(f"✅ Ollama available at {ollama_base_url} with model {ollama_model}")
        else:
            logger.warning("⚠️ Ollama not available - using rule-based responses only")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama check failed: {e}")
            return False
    
    def is_portfolio_query(self, message: str) -> bool:
        """Detect if query is about portfolio analysis (rule-based)"""
        portfolio_keywords = [
            # Cap analysis
            'cap ratio', 'large cap', 'mid cap', 'small cap', 'market cap',
            'cap allocation', 'what are my cap', 'how much large',
            
            # Performance
            'performing', 'returns', 'profit', 'loss', 'gain',
            'underperform', 'best fund', 'worst fund', 'top fund',
            'lowest return', 'highest return',
            
            # Rebalancing
            'rebalance', 'should i rebalance', 'allocation', 'overweight',
            'underweight', 'diversif', 'concentrated',
            
            # Portfolio analysis
            'health score', 'portfolio health', 'analyze', 'expense ratio',
            'amc concentration', 'category breakdown'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in portfolio_keywords)
    
    async def process_query(self, message: str, portfolio_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Process query using hybrid approach
        
        Returns:
        - Rule-based response if portfolio query
        - AI response if general question
        - Fallback if both fail
        """
        
        # Check if this is a portfolio analysis query
        if self.is_portfolio_query(message) and portfolio_data:
            response = self._get_rule_based_response(message, portfolio_data)
            if response:
                return response
        
        # Fall back to AI for general questions
        if self.ollama_available:
            response = await self._get_ai_response(message)
            if response:
                return response
        
        # Final fallback
        return self._get_fallback_response(message)
    
    def _get_rule_based_response(self, message: str, portfolio_data: Dict[str, Any]) -> Optional[str]:
        """Generate response using rule-based system (FAST ⚡)"""
        try:
            holdings = portfolio_data.get('holdings', [])
            if not holdings:
                return None
            
            total_value = sum(h.get('current_value', 0) for h in holdings)
            
            message_lower = message.lower()
            
            # Cap Ratio Analysis
            if any(term in message_lower for term in ['cap ratio', 'cap allocation', 'what are my cap']):
                return self._analyze_cap_ratios(holdings, total_value)
            
            # Performance Analysis
            if any(term in message_lower for term in ['performing', 'best fund', 'worst fund', 'underperform', 'returns']):
                return self._analyze_performance(holdings)
            
            # Rebalancing Suggestion
            if any(term in message_lower for term in ['rebalance', 'should i rebalance']):
                return self._suggest_rebalancing(holdings, total_value)
            
            # Diversification Check
            if any(term in message_lower for term in ['diversif', 'concentrated', 'concentration']):
                return self._check_diversification(holdings, total_value)
            
            # Expense Ratio Analysis
            if 'expense ratio' in message_lower:
                return self._analyze_expense_ratios(holdings)
            
        except Exception as e:
            logger.error(f"Error in rule-based response: {e}")
        
        return None
    
    def _analyze_cap_ratios(self, holdings: List[Dict], total_value: float) -> str:
        """Analyze large/mid/small cap ratios"""
        large_cap_value = 0
        mid_cap_value = 0
        small_cap_value = 0
        
        # Simplified cap classification (you'd use actual market cap data)
        for h in holdings:
            # This is simplified - in production, use actual market cap data
            fund_name = h.get('fund_name', '').lower()
            value = h.get('current_value', 0)
            
            if 'large' in fund_name or 'bluechip' in fund_name or 'nifty' in fund_name:
                large_cap_value += value
            elif 'mid' in fund_name:
                mid_cap_value += value
            elif 'small' in fund_name or 'sectoral' in fund_name:
                small_cap_value += value
            else:
                large_cap_value += value  # Default to large cap
        
        total = large_cap_value + mid_cap_value + small_cap_value
        
        large_pct = (large_cap_value / total * 100) if total > 0 else 0
        mid_pct = (mid_cap_value / total * 100) if total > 0 else 0
        small_pct = (small_cap_value / total * 100) if total > 0 else 0
        
        response = f"""📊 **Your Capital Distribution:**

💰 Large Cap: {large_pct:.1f}% (₹{large_cap_value:,.0f})
📈 Mid Cap: {mid_pct:.1f}% (₹{mid_cap_value:,.0f})
🚀 Small Cap: {small_pct:.1f}% (₹{small_cap_value:,.0f})

**Analysis:**"""
        
        if large_pct > 70:
            response += "\n✅ Strong large cap base for stability"
        elif large_pct < 40:
            response += "\n⚠️ Low large cap exposure - consider adding for stability"
        else:
            response += "\n✅ Well-balanced cap allocation"
        
        if small_pct > 30:
            response += "\n⚠️ High small cap risk - consider trimming"
        elif small_pct > 0:
            response += "\n✅ Healthy small cap exposure for growth"
        
        return response
    
    def _analyze_performance(self, holdings: List[Dict]) -> str:
        """Analyze portfolio performance"""
        # Sort by returns
        sorted_holdings = sorted(holdings, key=lambda x: x.get('returns', 0))
        
        best = sorted_holdings[-1] if sorted_holdings else None
        worst = sorted_holdings[0] if sorted_holdings else None
        
        total_returns = sum(h.get('returns', 0) for h in holdings)
        total_invested = sum(h.get('invested_value', 0) for h in holdings)
        
        overall_return_pct = (total_returns / total_invested * 100) if total_invested > 0 else 0
        
        response = f"""📈 **Portfolio Performance:**

Overall Returns: ₹{total_returns:,.0f} ({overall_return_pct:+.2f}%)

**Best Performer:** {best.get('fund_name', 'N/A')}
  Returns: ₹{best.get('returns', 0):,.0f} ({best.get('return_pct', 0):+.2f}%)

**Needs Review:** {worst.get('fund_name', 'N/A')}
  Returns: ₹{worst.get('returns', 0):,.0f} ({worst.get('return_pct', 0):+.2f}%)"""
        
        return response
    
    def _suggest_rebalancing(self, holdings: List[Dict], total_value: float) -> str:
        """Suggest rebalancing strategy"""
        category_allocation = defaultdict(float)
        for h in holdings:
            category = h.get('category', 'Unknown')
            value = h.get('current_value', 0)
            category_allocation[category] += value
        
        equity_pct = sum(v for k, v in category_allocation.items() 
                        if 'equity' in k.lower()) / total_value * 100 if total_value > 0 else 0
        debt_pct = sum(v for k, v in category_allocation.items() 
                      if 'debt' in k.lower()) / total_value * 100 if total_value > 0 else 0
        
        response = "⚖️ **Rebalancing Recommendation:**\n\n"
        response += f"Current Allocation:\n"
        response += f"- Equity: {equity_pct:.1f}%\n"
        response += f"- Debt: {debt_pct:.1f}%\n\n"
        
        if equity_pct > 80:
            response += "✅ Consider trimming equity funds (too much risk)"
        elif equity_pct < 40:
            response += "✅ Consider adding equity for growth"
        else:
            response += "✅ Allocation looks balanced!"
        
        return response
    
    def _check_diversification(self, holdings: List[Dict], total_value: float) -> str:
        """Check portfolio diversification"""
        num_holdings = len(holdings)
        
        amc_values = defaultdict(float)
        for h in holdings:
            amc = h.get('amc', 'Unknown')
            value = h.get('current_value', 0)
            amc_values[amc] += value
        
        max_amc_concentration = max((v / total_value * 100) for v in amc_values.values()) if amc_values else 0
        
        response = f"""🎨 **Diversification Analysis:**

Holdings: {num_holdings} funds
AMCs: {len(amc_values)} different companies

**Concentration:** Highest AMC: {max_amc_concentration:.1f}%

"""
        
        if num_holdings < 5:
            response += "⚠️ Limited diversification - consider adding 3-5 more funds"
        else:
            response += "✅ Good diversification"
        
        if max_amc_concentration > 40:
            response += f"\n⚠️ High AMC concentration - spread across more AMCs"
        else:
            response += f"\n✅ Well-spread across AMCs"
        
        return response
    
    def _analyze_expense_ratios(self, holdings: List[Dict]) -> str:
        """Analyze expense ratios"""
        response = "💸 **Expense Ratio Analysis:**\n\n"
        response += "Your funds have expense ratios between 0.5% - 2.5% typically.\n\n"
        response += "💡 Lower is better - more returns for you!\n"
        response += "- Index Funds: 0.1-0.5%\n"
        response += "- Actively Managed: 0.8-2.5%\n"
        response += "- Sectoral Funds: 1-2.5%\n"
        return response
    
    async def _get_ai_response(self, message: str) -> Optional[str]:
        """Get response from TinyLlama via Ollama"""
        if not self.ollama_available or not REQUESTS_AVAILABLE:
            return None
        
        try:
            system_prompt = """You are a helpful mutual fund assistant. 
Answer questions about mutual funds, SIP, investing strategies, and personal finance.
Be concise and helpful. If you don't know something, say so.
Keep responses to 2-3 sentences max for chat."""
            
            full_prompt = f"{system_prompt}\n\nQuestion: {message}"
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "num_ctx": 256,  # Context window
                    "top_k": 40,
                    "top_p": 0.9,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', '').strip()
                
                # Clean up response
                ai_response = re.sub(r'\n\n+', '\n', ai_response)  # Remove multiple newlines
                
                return ai_response if ai_response else None
                
        except Exception as e:
            logger.error(f"Error getting AI response from Ollama: {e}")
        
        return None
    
    def _get_fallback_response(self, message: str) -> str:
        """Fallback response when AI and rule-based both fail"""
        message_lower = message.lower()
        
        fallback_responses = {
            'sip': "SIP (Systematic Investment Plan) is investing a fixed amount regularly. Great for rupee cost averaging!",
            'equity': "Equity funds invest in stocks. Higher returns but more risk. For 5+ year goals.",
            'debt': "Debt funds invest in fixed income. Lower risk, stable returns. For short-term goals.",
            'index': "Index funds track market indices like Nifty 50. Low fees, good returns, great for beginners!",
            'mutual fund': "Mutual funds pool money from many investors to buy securities. Professionally managed.",
            'diversif': "Diversification means spreading investments across different funds/sectors to reduce risk.",
            'expense ratio': "Annual fee fund houses charge. Lower % = more returns for you!",
        }
        
        for keyword, response in fallback_responses.items():
            if keyword in message_lower:
                return response
        
        return "I can help with your mutual fund questions! Ask me about SIP, diversification, fund types, or upload your portfolio for detailed analysis."


# Global instance
hybrid_ai = HybridAIService()
