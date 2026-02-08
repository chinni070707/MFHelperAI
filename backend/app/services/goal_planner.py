"""
Goal-Based Planning - AI-powered financial goal planning
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
import math

# AI service removed - using non-AI strategy
# from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class GoalType(str, Enum):
    RETIREMENT = "retirement"
    HOUSE = "house"
    EDUCATION = "education"
    CAR = "car"
    VACATION = "vacation"
    EMERGENCY_FUND = "emergency_fund"
    WEDDING = "wedding"
    CUSTOM = "custom"


class GoalPlanner:
    """AI-powered goal-based investment planning"""
    
    # Assumed annual returns
    EQUITY_RETURN = 12.0  # %
    DEBT_RETURN = 7.0  # %
    HYBRID_RETURN = 10.0  # %
    INFLATION = 6.0  # %
    
    def __init__(self):
        pass
    
    async def create_goal_plan(
        self,
        goal_name: str,
        goal_type: str,
        target_amount: float,
        time_horizon: int,  # years
        current_portfolio_value: float = 0,
        monthly_investment: float = 0,
        risk_tolerance: str = "moderate",  # low, moderate, high
        user_age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive goal-based investment plan
        """
        try:
            # Calculate required parameters
            future_value = self._adjust_for_inflation(target_amount, time_horizon)
            
            # Calculate required monthly SIP
            required_monthly_sip = self._calculate_required_sip(
                future_value,
                time_horizon,
                current_portfolio_value,
                risk_tolerance
            )
            
            # Calculate projected value with current investment
            projected_value = self._calculate_future_value(
                current_portfolio_value,
                monthly_investment,
                time_horizon,
                risk_tolerance
            )
            
            # Calculate gap
            gap = future_value - projected_value
            gap_percentage = (gap / future_value * 100) if future_value > 0 else 0
            
            # Generate allocation strategy
            allocation = self._get_allocation_strategy(risk_tolerance, time_horizon)
            
            # Get AI-powered insights and recommendations
            ai_insights = await self._get_ai_goal_insights(
                goal_name,
                goal_type,
                target_amount,
                future_value,
                time_horizon,
                gap,
                required_monthly_sip,
                monthly_investment,
                allocation
            )
            
            # Generate milestones
            milestones = self._generate_milestones(
                future_value,
                time_horizon,
                required_monthly_sip,
                allocation
            )
            
            return {
                "goal_name": goal_name,
                "goal_type": goal_type,
                "target_amount": target_amount,
                "time_horizon_years": time_horizon,
                "inflation_adjusted_amount": round(future_value, 2),
                "current_value": current_portfolio_value,
                "monthly_investment": monthly_investment,
                "required_monthly_sip": round(required_monthly_sip, 2),
                "projected_value": round(projected_value, 2),
                "gap": round(gap, 2),
                "gap_percentage": round(gap_percentage, 1),
                "on_track": gap <= 0,
                "allocation_strategy": allocation,
                "milestones": milestones,
                "insights": ai_insights.get('insights', []),
                "recommendations": ai_insights.get('recommendations', []),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating goal plan: {e}")
            return {
                "error": "Failed to create goal plan",
                "message": str(e)
            }
    
    def _adjust_for_inflation(self, amount: float, years: int) -> float:
        """Adjust target amount for inflation"""
        return amount * math.pow(1 + self.INFLATION / 100, years)
    
    def _calculate_required_sip(
        self,
        future_value: float,
        years: int,
        current_value: float,
        risk_tolerance: str
    ) -> float:
        """Calculate required monthly SIP"""
        # Determine expected return based on risk tolerance
        if risk_tolerance == "high":
            annual_return = self.EQUITY_RETURN
        elif risk_tolerance == "low":
            annual_return = self.DEBT_RETURN
        else:
            annual_return = self.HYBRID_RETURN
        
        monthly_rate = annual_return / 12 / 100
        months = years * 12
        
        # Future value of current portfolio
        fv_current = current_value * math.pow(1 + annual_return / 100, years)
        
        # Remaining amount needed
        remaining = future_value - fv_current
        
        if remaining <= 0:
            return 0
        
        # Calculate SIP using future value of annuity formula
        # FV = P * [((1 + r)^n - 1) / r] * (1 + r)
        if monthly_rate > 0:
            sip = remaining / (((math.pow(1 + monthly_rate, months) - 1) / monthly_rate) * (1 + monthly_rate))
        else:
            sip = remaining / months
        
        return max(0, sip)
    
    def _calculate_future_value(
        self,
        current_value: float,
        monthly_sip: float,
        years: int,
        risk_tolerance: str
    ) -> float:
        """Calculate future value of current investment + SIP"""
        if risk_tolerance == "high":
            annual_return = self.EQUITY_RETURN
        elif risk_tolerance == "low":
            annual_return = self.DEBT_RETURN
        else:
            annual_return = self.HYBRID_RETURN
        
        monthly_rate = annual_return / 12 / 100
        months = years * 12
        
        # Future value of current portfolio
        fv_current = current_value * math.pow(1 + annual_return / 100, years)
        
        # Future value of SIP
        if monthly_rate > 0:
            fv_sip = monthly_sip * (((math.pow(1 + monthly_rate, months) - 1) / monthly_rate) * (1 + monthly_rate))
        else:
            fv_sip = monthly_sip * months
        
        return fv_current + fv_sip
    
    def _get_allocation_strategy(self, risk_tolerance: str, years: int) -> Dict[str, float]:
        """Determine asset allocation based on risk and time horizon"""
        if risk_tolerance == "high" or years > 10:
            return {
                "equity": 80,
                "debt": 15,
                "gold": 5
            }
        elif risk_tolerance == "low" or years < 3:
            return {
                "equity": 30,
                "debt": 60,
                "gold": 10
            }
        else:  # moderate
            if years > 5:
                return {
                    "equity": 60,
                    "debt": 30,
                    "gold": 10
                }
            else:
                return {
                    "equity": 40,
                    "debt": 50,
                    "gold": 10
                }
    
    def _generate_milestones(
        self,
        target_amount: float,
        years: int,
        monthly_sip: float,
        allocation: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Generate milestone checkpoints"""
        milestones = []
        
        # Create milestones at 25%, 50%, 75%, 100%
        percentages = [25, 50, 75, 100]
        
        for pct in percentages:
            milestone_years = (years * pct) / 100
            milestone_date = datetime.utcnow() + timedelta(days=milestone_years * 365)
            milestone_value = (target_amount * pct) / 100
            
            milestones.append({
                "percentage": pct,
                "target_value": round(milestone_value, 2),
                "target_date": milestone_date.strftime("%b %Y"),
                "years_from_now": round(milestone_years, 1),
                "status": "pending"
            })
        
        return milestones
    
    async def _get_ai_goal_insights(
        self,
        goal_name: str,
        goal_type: str,
        target_amount: float,
        inflation_adjusted: float,
        years: int,
        gap: float,
        required_sip: float,
        current_sip: float,
        allocation: Dict[str, float]
    ) -> Dict[str, Any]:
        """Get AI-powered insights for goal"""
        # AI service removed - use rule-based insights
        if True:  # not ai_service.is_available():
            return self._get_rule_based_goal_insights(gap, required_sip, current_sip)
        
        # Dead code below - AI service removed, prompt no longer used
        # try:
        #     prompt = f"""Analyze this financial goal..."""
        #     response = await ai_service.generate_completion(...)
        # except Exception as e:
        #     logger.error(f\"Error getting AI goal insights: {e}\")
        
        return self._get_rule_based_goal_insights(gap, required_sip, current_sip)
    
    def _get_rule_based_goal_insights(
        self,
        gap: float,
        required_sip: float,
        current_sip: float
    ) -> Dict[str, Any]:
        """Fallback rule-based insights"""
        insights = []
        recommendations = []
        
        if gap <= 0:
            insights.append("✅ You're on track to achieve this goal with current investments!")
            insights.append(f"🎯 Continue investing ₹{current_sip:,.0f}/month to stay on track")
            recommendations.append("Maintain your current investment discipline")
            recommendations.append("Review progress quarterly and rebalance annually")
        else:
            gap_pct = (required_sip - current_sip) / current_sip * 100 if current_sip > 0 else 100
            insights.append(f"⚠️ You need to increase monthly investment by ₹{required_sip - current_sip:,.0f}")
            insights.append(f"📊 Current investment is {100 - gap_pct:.0f}% of required amount")
            
            recommendations.append(f"Increase SIP to ₹{required_sip:,.0f}/month")
            recommendations.append("Consider allocating bonuses/increments to close the gap")
            recommendations.append("Review and cut unnecessary expenses to free up funds")
        
        return {
            "insights": insights,
            "recommendations": recommendations
        }


# Global goal planner instance
goal_planner = GoalPlanner()
