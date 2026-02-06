"""
Analysis Routes - New standalone analysis features for overlap, goal checker, and stock allocation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

# Setup logger
logger = logging.getLogger(__name__)

router = APIRouter()

# ============ Request Models ============

class OverlapRequest(BaseModel):
    funds: List[str]

class GoalCheckerRequest(BaseModel):
    goal_name: str
    current_corpus: float
    target_amount: float
    years: int
    monthly_sip: Optional[float] = 0

class FundAllocation(BaseModel):
    name: str
    amount: float

class StockAllocationRequest(BaseModel):
    funds: List[FundAllocation]


# ============ Overlap Analysis ============

@router.post("/overlap")
async def analyze_overlap(request: OverlapRequest):
    """
    Analyze overlap between multiple mutual funds
    Returns common stocks and their weightages
    """
    try:
        logger.info(f"Analyzing overlap for {len(request.funds)} funds")
        
        if len(request.funds) < 2:
            raise HTTPException(status_code=400, detail="At least 2 funds required for overlap analysis")
        
        # Demo data - In production, this would fetch real holdings from database
        demo_holdings = {
            "HDFC Top 100 Fund": {
                "stocks": [
                    {"name": "Reliance Industries", "weight": 8.5},
                    {"name": "HDFC Bank", "weight": 7.2},
                    {"name": "Infosys", "weight": 6.8},
                    {"name": "ICICI Bank", "weight": 5.4},
                    {"name": "TCS", "weight": 5.1}
                ]
            },
            "Axis Bluechip Fund": {
                "stocks": [
                    {"name": "Reliance Industries", "weight": 7.8},
                    {"name": "HDFC Bank", "weight": 6.9},
                    {"name": "Infosys", "weight": 5.2},
                    {"name": "ICICI Bank", "weight": 4.8},
                    {"name": "Bharti Airtel", "weight": 4.3}
                ]
            },
            "Parag Parikh Flexi Cap": {
                "stocks": [
                    {"name": "Reliance Industries", "weight": 6.5},
                    {"name": "HDFC Bank", "weight": 5.8},
                    {"name": "Alphabet Inc", "weight": 5.5},
                    {"name": "Microsoft", "weight": 4.2},
                    {"name": "Asian Paints", "weight": 3.8}
                ]
            },
            "Mirae Asset Large Cap": {
                "stocks": [
                    {"name": "Reliance Industries", "weight": 8.2},
                    {"name": "HDFC Bank", "weight": 6.5},
                    {"name": "ICICI Bank", "weight": 5.9},
                    {"name": "Infosys", "weight": 5.4},
                    {"name": "Kotak Mahindra Bank", "weight": 4.1}
                ]
            }
        }
        
        # Calculate overlaps
        overlaps = []
        for i, fund1 in enumerate(request.funds):
            for fund2 in request.funds[i+1:]:
                # Get holdings for both funds (use demo data or default)
                holdings1 = demo_holdings.get(fund1, demo_holdings["HDFC Top 100 Fund"])["stocks"]
                holdings2 = demo_holdings.get(fund2, demo_holdings["Axis Bluechip Fund"])["stocks"]
                
                # Find common stocks
                stocks1_names = {s["name"] for s in holdings1}
                stocks2_names = {s["name"] for s in holdings2}
                common_names = stocks1_names.intersection(stocks2_names)
                
                common_stocks = []
                for name in common_names:
                    weight1 = next((s["weight"] for s in holdings1 if s["name"] == name), 0)
                    weight2 = next((s["weight"] for s in holdings2 if s["name"] == name), 0)
                    avg_weight = (weight1 + weight2) / 2
                    common_stocks.append({
                        "name": name,
                        "weight": round(avg_weight, 2)
                    })
                
                # Sort by weight
                common_stocks.sort(key=lambda x: x["weight"], reverse=True)
                
                # Calculate overlap percentage
                overlap_pct = len(common_names) / max(len(stocks1_names), len(stocks2_names)) * 100
                
                overlaps.append({
                    "funds": [fund1, fund2],
                    "overlap": round(overlap_pct, 1),
                    "commonStocks": common_stocks
                })
        
        return {
            "status": "success",
            "overlaps": overlaps,
            "total_funds": len(request.funds)
        }
        
    except Exception as e:
        logger.error(f"Error in overlap analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Goal Checker ============

@router.post("/goal-checker")
async def calculate_goal(request: GoalCheckerRequest):
    """
    Calculate required CAGR to achieve financial goals
    """
    try:
        logger.info(f"Calculating goal: {request.goal_name}")
        
        if request.current_corpus <= 0 or request.target_amount <= 0 or request.years <= 0:
            raise HTTPException(status_code=400, detail="Invalid input values")
        
        # Calculate CAGR without SIP
        cagr = ((request.target_amount / request.current_corpus) ** (1 / request.years) - 1) * 100
        
        # If SIP is included, calculate adjusted return
        required_return = cagr
        if request.monthly_sip > 0:
            total_sip = request.monthly_sip * 12 * request.years
            adjusted_target = request.target_amount - total_sip
            if adjusted_target > request.current_corpus:
                required_return = ((adjusted_target / request.current_corpus) ** (1 / request.years) - 1) * 100
            else:
                required_return = 8.0  # Minimum expected return
        
        # Generate advice based on CAGR
        advice = []
        if required_return <= 10:
            advice = [
                "Achievable with conservative investments",
                "Consider balanced funds or debt-heavy hybrid funds",
                "Risk Level: Low to Moderate"
            ]
        elif required_return <= 15:
            advice = [
                "Realistic with equity investments",
                "Focus on diversified equity mutual funds",
                "Consider a mix of large-cap, mid-cap, and flexi-cap funds",
                "Risk Level: Moderate"
            ]
        elif required_return <= 20:
            advice = [
                "Aggressive target - requires higher risk appetite",
                "Consider mid-cap and small-cap funds",
                "Risk Level: High",
                "Diversify across 4-5 funds to manage risk"
            ]
        else:
            advice = [
                "Very aggressive target - may not be realistic with mutual funds alone",
                "Consider increasing monthly SIP contribution",
                "Exploring direct equity investments (higher risk)",
                "Reviewing if the target amount is realistic"
            ]
        
        return {
            "status": "success",
            "goal_name": request.goal_name,
            "current_corpus": request.current_corpus,
            "target_amount": request.target_amount,
            "years": request.years,
            "monthly_sip": request.monthly_sip,
            "required_cagr": round(required_return, 2),
            "growth_multiplier": round(request.target_amount / request.current_corpus, 2),
            "advice": advice
        }
        
    except Exception as e:
        logger.error(f"Error in goal calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Stock Allocation ============

@router.post("/stock-allocation")
async def analyze_stock_allocation(request: StockAllocationRequest):
    """
    Analyze stock-wise allocation across multiple mutual funds
    Shows which stocks are common and their cumulative exposure
    """
    try:
        logger.info(f"Analyzing stock allocation for {len(request.funds)} funds")
        
        if not request.funds:
            raise HTTPException(status_code=400, detail="At least one fund required")
        
        # Demo holdings data
        demo_fund_holdings = {
            "HDFC Top 100 Fund": [
                {"name": "Reliance Industries", "sector": "Energy", "weight": 8.5},
                {"name": "HDFC Bank", "sector": "Banking", "weight": 7.2},
                {"name": "Infosys", "sector": "IT", "weight": 6.8},
                {"name": "ICICI Bank", "sector": "Banking", "weight": 5.4},
                {"name": "TCS", "sector": "IT", "weight": 5.1},
                {"name": "Bharti Airtel", "sector": "Telecom", "weight": 4.3},
                {"name": "Asian Paints", "sector": "Consumer", "weight": 3.5}
            ]
        }
        
        # Aggregate stocks across all funds
        stock_aggregation = {}
        total_portfolio = sum(fund.amount for fund in request.funds)
        
        for fund in request.funds:
            # Get holdings (use demo data)
            holdings = demo_fund_holdings.get(fund.name, demo_fund_holdings["HDFC Top 100 Fund"])
            fund_weight = fund.amount / total_portfolio
            
            for stock in holdings:
                stock_name = stock["name"]
                if stock_name not in stock_aggregation:
                    stock_aggregation[stock_name] = {
                        "name": stock_name,
                        "sector": stock["sector"],
                        "total_weight": 0,
                        "funds": []
                    }
                
                # Add weighted exposure
                stock_exposure = stock["weight"] * fund_weight
                stock_aggregation[stock_name]["total_weight"] += stock_exposure
                stock_aggregation[stock_name]["funds"].append(fund.name)
        
        # Sort by total weight
        stocks = sorted(stock_aggregation.values(), key=lambda x: x["total_weight"], reverse=True)
        
        # Calculate summary
        common_stocks = sum(1 for s in stocks if len(s["funds"]) > 1)
        
        # Sector analysis
        sector_totals = {}
        for stock in stocks:
            sector = stock["sector"]
            sector_totals[sector] = sector_totals.get(sector, 0) + stock["total_weight"]
        
        top_sector = max(sector_totals.items(), key=lambda x: x[1])[0] if sector_totals else "N/A"
        
        return {
            "status": "success",
            "total_portfolio": total_portfolio,
            "total_unique_stocks": len(stocks),
            "common_stocks": common_stocks,
            "top_sector": top_sector,
            "stocks": [
                {
                    "name": s["name"],
                    "sector": s["sector"],
                    "weight": round(s["total_weight"], 2),
                    "funds": s["funds"]
                }
                for s in stocks[:15]  # Top 15 stocks
            ],
            "sector_allocation": {k: round(v, 2) for k, v in sector_totals.items()}
        }
        
    except Exception as e:
        logger.error(f"Error in stock allocation analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
