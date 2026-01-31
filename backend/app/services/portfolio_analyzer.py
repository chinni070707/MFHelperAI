"""
Portfolio Health Analyzer - AI-powered portfolio analysis
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from collections import defaultdict

from app.services.ai_service import ai_service
from app.config_ai import ai_settings

logger = logging.getLogger(__name__)


class PortfolioHealthAnalyzer:
    """Analyzes portfolio health and generates insights"""
    
    def __init__(self):
        self.weights = ai_settings.HEALTH_SCORE_WEIGHTS
    
    async def analyze_portfolio(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive portfolio analysis
        Returns health score, insights, and recommendations
        """
        try:
            holdings = portfolio_data.get('holdings', [])
            if not holdings:
                return self._empty_analysis()
            
            # Calculate individual scores
            diversification_score = self._calculate_diversification_score(holdings)
            allocation_score = self._calculate_allocation_score(holdings)
            performance_score = self._calculate_performance_score(holdings)
            risk_score = self._calculate_risk_score(holdings)
            cost_score = self._calculate_cost_score(holdings)
            
            # Calculate overall health score (0-100)
            health_score = (
                diversification_score * self.weights['diversification'] +
                allocation_score * self.weights['allocation'] +
                performance_score * self.weights['performance'] +
                risk_score * self.weights['risk'] +
                cost_score * self.weights['cost']
            )
            
            # Generate insights
            insights = self._generate_insights(
                holdings,
                diversification_score,
                allocation_score,
                performance_score,
                risk_score,
                cost_score
            )
            
            # Get AI-powered recommendations
            recommendations = await self._get_ai_recommendations(
                portfolio_data,
                health_score,
                insights
            )
            
            return {
                "health_score": round(health_score, 1),
                "health_grade": self._get_health_grade(health_score),
                "scores": {
                    "diversification": round(diversification_score, 1),
                    "allocation": round(allocation_score, 1),
                    "performance": round(performance_score, 1),
                    "risk": round(risk_score, 1),
                    "cost": round(cost_score, 1)
                },
                "insights": insights,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat(),
                "holdings_count": len(holdings),
                "total_value": sum(h.get('current_value', 0) for h in holdings)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return self._empty_analysis()
    
    def _calculate_diversification_score(self, holdings: List[Dict]) -> float:
        """Score based on diversification (0-100)"""
        if not holdings:
            return 0.0
        
        score = 100.0
        
        # Check number of holdings
        num_holdings = len(holdings)
        if num_holdings < 5:
            score -= 20
        elif num_holdings > 20:
            score -= 10  # Too many can be hard to manage
        
        # Check AMC concentration
        amc_values = defaultdict(float)
        total_value = sum(h.get('current_value', 0) for h in holdings)
        
        for holding in holdings:
            amc = holding.get('amc', 'Unknown')
            value = holding.get('current_value', 0)
            amc_values[amc] += value
        
        # Penalize if any single AMC > 40%
        for amc, value in amc_values.items():
            concentration = (value / total_value * 100) if total_value > 0 else 0
            if concentration > 40:
                score -= (concentration - 40)
        
        # Check category diversification
        categories = set(h.get('category', 'Unknown') for h in holdings)
        if len(categories) < 3:
            score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_allocation_score(self, holdings: List[Dict]) -> float:
        """Score based on asset allocation (0-100)"""
        if not holdings:
            return 0.0
        
        score = 100.0
        total_value = sum(h.get('current_value', 0) for h in holdings)
        
        # Calculate category allocation
        category_allocation = defaultdict(float)
        for holding in holdings:
            category = holding.get('category', 'Unknown')
            value = holding.get('current_value', 0)
            category_allocation[category] += value
        
        # Check for balanced allocation
        equity_allocation = sum(
            v for k, v in category_allocation.items()
            if 'equity' in k.lower() or 'stock' in k.lower()
        ) / total_value * 100 if total_value > 0 else 0
        
        debt_allocation = sum(
            v for k, v in category_allocation.items()
            if 'debt' in k.lower() or 'bond' in k.lower() or 'income' in k.lower()
        ) / total_value * 100 if total_value > 0 else 0
        
        # Ideal: Some debt allocation for stability
        if debt_allocation < 10:
            score -= 15
        elif debt_allocation > 50:
            score -= 10
        
        # Check if over-concentrated in one category
        for category, value in category_allocation.items():
            allocation_pct = (value / total_value * 100) if total_value > 0 else 0
            if allocation_pct > 60:
                score -= (allocation_pct - 60) * 0.5
        
        return max(0, min(100, score))
    
    def _calculate_performance_score(self, holdings: List[Dict]) -> float:
        """Score based on portfolio performance (0-100)"""
        if not holdings:
            return 0.0
        
        total_returns = sum(h.get('returns', 0) for h in holdings)
        total_invested = sum(h.get('invested_value', 0) for h in holdings)
        
        if total_invested == 0:
            return 50.0  # Neutral
        
        return_pct = (total_returns / total_invested * 100) if total_invested > 0 else 0
        
        # Score based on returns
        if return_pct < 0:
            score = max(0, 50 + return_pct * 2)  # Negative returns
        elif return_pct < 8:
            score = 50 + return_pct * 3  # Below market avg
        elif return_pct < 15:
            score = 75 + (return_pct - 8) * 2  # Good returns
        else:
            score = min(100, 90 + (return_pct - 15))  # Excellent returns
        
        return max(0, min(100, score))
    
    def _calculate_risk_score(self, holdings: List[Dict]) -> float:
        """Score based on risk assessment (0-100)"""
        if not holdings:
            return 0.0
        
        score = 100.0
        
        # Check for high-risk concentration
        total_value = sum(h.get('current_value', 0) for h in holdings)
        
        for holding in holdings:
            category = holding.get('category', '').lower()
            value = holding.get('current_value', 0)
            allocation_pct = (value / total_value * 100) if total_value > 0 else 0
            
            # Penalize high allocation to high-risk categories
            if 'small cap' in category or 'sectoral' in category:
                if allocation_pct > 20:
                    score -= (allocation_pct - 20) * 0.5
        
        return max(0, min(100, score))
    
    def _calculate_cost_score(self, holdings: List[Dict]) -> float:
        """Score based on expense ratios (0-100)"""
        if not holdings:
            return 0.0
        
        # Assuming expense ratio data is available (0.5% to 2.5% typical)
        # For now, return neutral score since we don't have this data
        return 75.0  # Default good score
    
    def _generate_insights(
        self,
        holdings: List[Dict],
        div_score: float,
        alloc_score: float,
        perf_score: float,
        risk_score: float,
        cost_score: float
    ) -> List[Dict[str, str]]:
        """Generate actionable insights"""
        insights = []
        total_value = sum(h.get('current_value', 0) for h in holdings)
        
        # Diversification insights
        if div_score < 70:
            num_holdings = len(holdings)
            if num_holdings < 5:
                insights.append({
                    "type": "warning",
                    "category": "diversification",
                    "message": f"⚠️ Limited diversification: Only {num_holdings} funds. Consider adding 3-5 more."
                })
            
            # Check AMC concentration
            amc_values = defaultdict(float)
            for holding in holdings:
                amc = holding.get('amc', 'Unknown')
                value = holding.get('current_value', 0)
                amc_values[amc] += value
            
            for amc, value in sorted(amc_values.items(), key=lambda x: x[1], reverse=True)[:1]:
                concentration = (value / total_value * 100) if total_value > 0 else 0
                if concentration > 40:
                    insights.append({
                        "type": "warning",
                        "category": "diversification",
                        "message": f"⚠️ High AMC concentration: {concentration:.1f}% in {amc}"
                    })
        else:
            insights.append({
                "type": "success",
                "category": "diversification",
                "message": f"✅ Good diversification across {len(holdings)} funds"
            })
        
        # Allocation insights
        category_allocation = defaultdict(float)
        for holding in holdings:
            category = holding.get('category', 'Unknown')
            value = holding.get('current_value', 0)
            category_allocation[category] += value
        
        equity_allocation = sum(
            v for k, v in category_allocation.items()
            if 'equity' in k.lower()
        ) / total_value * 100 if total_value > 0 else 0
        
        debt_allocation = sum(
            v for k, v in category_allocation.items()
            if 'debt' in k.lower()
        ) / total_value * 100 if total_value > 0 else 0
        
        if debt_allocation < 10:
            insights.append({
                "type": "opportunity",
                "category": "allocation",
                "message": f"💡 Consider adding debt funds: Currently {debt_allocation:.1f}% debt allocation"
            })
        
        if equity_allocation > 80:
            insights.append({
                "type": "warning",
                "category": "allocation",
                "message": f"⚠️ High equity exposure: {equity_allocation:.1f}% - Consider rebalancing"
            })
        
        # Performance insights
        total_returns = sum(h.get('returns', 0) for h in holdings)
        total_invested = sum(h.get('invested_value', 0) for h in holdings)
        return_pct = (total_returns / total_invested * 100) if total_invested > 0 else 0
        
        if perf_score >= 75:
            insights.append({
                "type": "success",
                "category": "performance",
                "message": f"✅ Strong performance: {return_pct:+.2f}% returns"
            })
        elif perf_score < 50:
            insights.append({
                "type": "warning",
                "category": "performance",
                "message": f"⚠️ Underperforming: {return_pct:+.2f}% returns - Review fund selections"
            })
        
        return insights[:5]  # Return top 5 insights
    
    async def _get_ai_recommendations(
        self,
        portfolio_data: Dict[str, Any],
        health_score: float,
        insights: List[Dict]
    ) -> List[str]:
        """Get AI-powered recommendations"""
        if not ai_service.is_available():
            return self._get_rule_based_recommendations(health_score, insights)
        
        try:
            holdings = portfolio_data.get('holdings', [])
            total_value = sum(h.get('current_value', 0) for h in holdings)
            total_returns = sum(h.get('returns', 0) for h in holdings)
            
            prompt = f"""Analyze this mutual fund portfolio and provide 3-4 specific, actionable recommendations.

Portfolio Summary:
- Holdings: {len(holdings)} funds
- Total Value: ₹{total_value:,.0f}
- Total Returns: ₹{total_returns:,.0f}
- Health Score: {health_score}/100

Key Insights:
{chr(10).join([f"- {i['message']}" for i in insights[:3]])}

Provide recommendations as a JSON array of strings. Each recommendation should be:
1. Specific and actionable
2. Explain WHY it's needed
3. Include expected impact

Format: {{"recommendations": ["recommendation1", "recommendation2", ...]}}
"""
            
            system_message = "You are a financial advisor specializing in Indian mutual funds. Provide practical, actionable advice."
            
            response = await ai_service.generate_completion(
                prompt=prompt,
                system_message=system_message,
                max_tokens=500,
                temperature=0.7,
                json_mode=True
            )
            
            if response:
                import json
                data = json.loads(response)
                return data.get('recommendations', [])[:4]
            
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {e}")
        
        return self._get_rule_based_recommendations(health_score, insights)
    
    def _get_rule_based_recommendations(
        self,
        health_score: float,
        insights: List[Dict]
    ) -> List[str]:
        """Fallback rule-based recommendations"""
        recommendations = []
        
        if health_score < 60:
            recommendations.append(
                "📊 Overall portfolio health needs improvement. Focus on diversification and allocation first."
            )
        
        for insight in insights:
            if insight['type'] == 'warning':
                if 'diversification' in insight['category']:
                    recommendations.append(
                        "🎯 Increase diversification: Add funds from different AMCs and categories to reduce concentration risk."
                    )
                elif 'allocation' in insight['category']:
                    recommendations.append(
                        "⚖️ Rebalance allocation: Consider adding debt funds for stability and reducing equity exposure."
                    )
                elif 'performance' in insight['category']:
                    recommendations.append(
                        "📈 Review underperforming funds: Compare with category benchmarks and consider switching."
                    )
        
        if not recommendations:
            recommendations.append(
                "✨ Portfolio is well-structured! Continue monitoring and rebalance annually."
            )
        
        return recommendations[:4]
    
    def _get_health_grade(self, score: float) -> str:
        """Convert score to grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            "health_score": 0.0,
            "health_grade": "N/A",
            "scores": {
                "diversification": 0.0,
                "allocation": 0.0,
                "performance": 0.0,
                "risk": 0.0,
                "cost": 0.0
            },
            "insights": [],
            "recommendations": [],
            "analyzed_at": datetime.utcnow().isoformat(),
            "holdings_count": 0,
            "total_value": 0
        }


# Global analyzer instance
portfolio_analyzer = PortfolioHealthAnalyzer()
