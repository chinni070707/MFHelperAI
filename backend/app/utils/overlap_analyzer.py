"""
Enhanced Mutual Fund Overlap Analysis Utility
Provides comprehensive overlap analysis with actionable insights
"""
import json
from typing import List, Dict
from pathlib import Path
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class OverlapAnalyzer:
    """Analyzes overlapping holdings between mutual funds"""
    
    def __init__(self, holdings_file: str = None):
        """Initialize with fund holdings data"""
        if holdings_file is None:
            # Try multiple paths to find the data file
            from pathlib import Path
            possible_paths = [
                Path("backend/data/fund_holdings.json"),
                Path("data/fund_holdings.json"),
                Path("app/data/fund_holdings.json"),
                Path(__file__).parent.parent.parent / "data" / "fund_holdings.json"
            ]
            for  path in possible_paths:
                if path.exists():
                    holdings_file = str(path)
                    break
            if holdings_file is None:
                holdings_file = "data/fund_holdings.json"  # Fallback
        
        self.fund_data = self._load_holdings(holdings_file)
    
    def _load_holdings(self, file_path: str) -> Dict:
        """Load fund holdings from JSON file"""
        try:
            path = Path(file_path)
            with open(path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data['funds'])} funds from {file_path}")
            return data['funds']
        except Exception as e:
            logger.error(f"Error loading holdings: {str(e)}")
            return {}
    
    def get_fund_list(self) -> List[Dict]:
        """Get list of available funds"""
        funds = []
        for key, data in self.fund_data.items():
            funds.append({
                "key": key,
                "name": data["name"],
                "amc": data["amc"],
                "category": data["category"],
                "holdings_count": len(data.get("holdings", []))
            })
        return sorted(funds, key=lambda x: x["name"])
    
    def get_fund_holdings(self, fund_key: str) -> Dict:
        """Get holdings for a specific fund"""
        if fund_key not in self.fund_data:
            return None
        return self.fund_data[fund_key]
    
    def calculate_pairwise_overlap(self, fund_keys: List[str]) -> List[Dict]:
        """Calculate overlap between all pairs of funds"""
        overlaps = []
        
        for i, key1 in enumerate(fund_keys):
            for key2 in fund_keys[i+1:]:
                overlap = self._calculate_single_overlap(key1, key2)
                if overlap:
                    overlaps.append(overlap)
        
        return sorted(overlaps, key=lambda x: x["overlap_percentage"], reverse=True)
    
    def _calculate_single_overlap(self, fund_key1: str, fund_key2: str) -> Dict:
        """Calculate overlap between two funds"""
        fund1 = self.fund_data.get(fund_key1)
        fund2 = self.fund_data.get(fund_key2)
        
        if not fund1 or not fund2:
            return None
        
        # Get holdings
        holdings1 = {h["stock"]: h["weight"] for h in fund1.get("holdings", [])}
        holdings2 = {h["stock"]: h["weight"] for h in fund2.get("holdings", [])}
        
        # Find common stocks
        common_stocks = set(holdings1.keys()) & set(holdings2.keys())
        
        # Calculate overlap details
        common_details = []
        total_overlap_weight = 0
        
        for stock in common_stocks:
            weight1 = holdings1[stock]
            weight2 = holdings2[stock]
            avg_weight = (weight1 + weight2) / 2
            
            # Get sector
            sector1 = next((h["sector"] for h in fund1["holdings"] if h["stock"] == stock), "Unknown")
            
            common_details.append({
                "stock": stock,
                "sector": sector1,
                "weight_fund1": round(weight1, 2),
                "weight_fund2": round(weight2, 2),
                "avg_weight": round(avg_weight, 2)
            })
            total_overlap_weight += avg_weight
        
        # Sort by average weight
        common_details.sort(key=lambda x: x["avg_weight"], reverse=True)
        
        # Calculate overlap percentage
        # Method 1: Count-based (simple)
        count_based = (len(common_stocks) / max(len(holdings1), len(holdings2))) * 100
        
        # Method 2: Weight-based (more accurate)
        weight_based = (total_overlap_weight / 100) * 100  # Normalized to percentage
        
        # Calculate sector overlap
        sector_overlap = self._calculate_sector_overlap(fund1, fund2, common_details)
        
        return {
            "fund1": {
                "key": fund_key1,
                "name": fund1["name"],
                "amc": fund1["amc"]
            },
            "fund2": {
                "key": fund_key2,
                "name": fund2["name"],
                "amc": fund2["amc"]
            },
            "overlap_percentage": round(count_based, 1),
            "weight_overlap_percentage": round(weight_based, 1),
            "common_stocks_count": len(common_stocks),
            "total_stocks_fund1": len(holdings1),
            "total_stocks_fund2": len(holdings2),
            "common_stocks": common_details[:10],  # Top 10
            "sector_overlap": sector_overlap,
            "risk_level": self._assess_overlap_risk(count_based),
            "recommendation": self._get_recommendation(count_based, fund1, fund2)
        }
    
    def calculate_portfolio_overlap(self, fund_keys: List[str]) -> Dict:
        """Calculate overall portfolio overlap statistics"""
        if len(fund_keys) < 2:
            return {"error": "At least 2 funds required"}
        
        # Collect all stocks across all funds
        all_stocks = defaultdict(list)  # stock -> [(fund, weight, sector)]
        fund_details = {}
        
        for key in fund_keys:
            fund = self.fund_data.get(key)
            if not fund:
                continue
            
            fund_details[key] = fund["name"]
            for holding in fund.get("holdings", []):
                all_stocks[holding["stock"]].append({
                    "fund": fund["name"],
                    "weight": holding["weight"],
                    "sector": holding["sector"]
                })
        
        # Analyze stock concentration
        stock_analysis = []
        for stock, appearances in all_stocks.items():
            if len(appearances) > 1:  # Only overlapping stocks
                stock_analysis.append({
                    "stock": stock,
                    "sector": appearances[0]["sector"],
                    "appears_in": len(appearances),
                    "fund_count": len(appearances),
                    "funds": [a["fund"] for a in appearances],
                    "fund_weights": {a["fund"]: a["weight"] for a in appearances},
                    "total_weight": sum(a["weight"] for a in appearances),
                    "avg_weight": round(sum(a["weight"] for a in appearances) / len(appearances), 2),
                    "concentration_risk": "High" if len(appearances) >= len(fund_keys) * 0.7 else "Medium"
                })
        
        # Sort by number of appearances and weight
        stock_analysis.sort(key=lambda x: (x["appears_in"], x["avg_weight"]), reverse=True)
        
        # Compute pairwise overlap between all fund pairs
        pairwise_overlap = []
        fund_key_list = [k for k in fund_keys if k in fund_details]
        for i in range(len(fund_key_list)):
            for j in range(i + 1, len(fund_key_list)):
                k1, k2 = fund_key_list[i], fund_key_list[j]
                f1 = self.fund_data[k1]
                f2 = self.fund_data[k2]
                stocks1 = {h["stock"] for h in f1.get("holdings", [])}
                stocks2 = {h["stock"] for h in f2.get("holdings", [])}
                common = stocks1 & stocks2
                union = stocks1 | stocks2
                pct = round((len(common) / len(union)) * 100, 1) if union else 0
                pairwise_overlap.append({
                    "fund1": fund_details[k1],
                    "fund2": fund_details[k2],
                    "overlap_pct": pct,
                    "common_count": len(common)
                })
        
        # Per-fund sector breakdown for pie charts
        fund_holdings_summary = {}
        for key in fund_key_list:
            fund = self.fund_data[key]
            sector_weights = defaultdict(float)
            for h in fund.get("holdings", []):
                sector_weights[h["sector"]] += h["weight"]
            # Sort by weight desc, keep top 8 sectors + Others
            sorted_sectors = sorted(sector_weights.items(), key=lambda x: -x[1])
            top_sectors = sorted_sectors[:8]
            others = sum(w for _, w in sorted_sectors[8:])
            sectors = [{"sector": s, "weight": round(w, 2)} for s, w in top_sectors]
            if others > 0:
                sectors.append({"sector": "Others", "weight": round(others, 2)})
            fund_holdings_summary[fund["name"]] = {
                "key": key,
                "category": fund.get("category", ""),
                "amc": fund.get("amc", ""),
                "total_holdings": len(fund.get("holdings", [])),
                "sectors": sectors
            }
        
        # Sector-wise overlap
        sector_overlap = defaultdict(lambda: {"stocks": [], "total_weight": 0})
        for stock in stock_analysis:
            sector = stock["sector"]
            sector_overlap[sector]["stocks"].append(stock["stock"])
            sector_overlap[sector]["total_weight"] += stock["total_weight"]
        
        # Generate insights
        insights = self._generate_portfolio_insights(stock_analysis, sector_overlap, len(fund_keys))
        
        return {
            "total_funds": len(fund_keys),
            "unique_stocks": len(all_stocks),
            "overlapping_stocks": len(stock_analysis),
            "overlap_ratio": round((len(stock_analysis) / len(all_stocks)) * 100, 1) if all_stocks else 0,
            "top_overlapping_stocks": stock_analysis[:20],
            "sector_concentration": dict(sector_overlap),
            "insights": insights,
            "diversification_score": self._calculate_diversification_score(stock_analysis, len(fund_keys)),
            "pairwise_overlap": pairwise_overlap,
            "fund_holdings_summary": fund_holdings_summary,
            "fund_names": {k: fund_details[k] for k in fund_key_list}
        }
    
    def _calculate_sector_overlap(self, fund1: Dict, fund2: Dict, common_stocks: List[Dict]) -> Dict:
        """Calculate sector-wise overlap"""
        sector_overlap = defaultdict(int)
        for stock in common_stocks:
            sector_overlap[stock["sector"]] += 1
        
        return dict(sector_overlap)
    
    def _assess_overlap_risk(self, overlap_pct: float) -> str:
        """Assess risk level based on overlap percentage"""
        if overlap_pct >= 70:
            return "Very High"
        elif overlap_pct >= 50:
            return "High"
        elif overlap_pct >= 30:
            return "Medium"
        else:
            return "Low"
    
    def _get_recommendation(self, overlap_pct: float, fund1: Dict, fund2: Dict) -> str:
        """Get recommendation based on overlap"""
        if overlap_pct >= 70:
            return f"Very high overlap detected. Consider removing one fund or diversifying into different categories."
        elif overlap_pct >= 50:
            return f"Significant overlap. These funds have similar investment strategies. Consider diversifying."
        elif overlap_pct >= 30:
            return f"Moderate overlap. This is acceptable but monitor for concentration in specific stocks/sectors."
        else:
            return f"Low overlap. Good diversification between these funds."
    
    def _generate_portfolio_insights(self, stock_analysis: List[Dict], sector_overlap: Dict, fund_count: int) -> List[Dict]:
        """Generate actionable insights"""
        insights = []
        
        # Check for stocks appearing in many funds
        high_concentration_stocks = [s for s in stock_analysis if s["appears_in"] >= fund_count * 0.7]
        if high_concentration_stocks:
            insights.append({
                "type": "concentration_risk",
                "severity": "high",
                "title": f"High Concentration: {len(high_concentration_stocks)} stocks",
                "message": f"{', '.join([s['stock'] for s in high_concentration_stocks[:3]])} appear in {high_concentration_stocks[0]['appears_in']}/{fund_count} funds.",
                "recommendation": "Consider the risk of over-concentration in these stocks."
            })
        
        # Check sector concentration
        dominant_sectors = sorted(sector_overlap.items(), key=lambda x: x[1]["total_weight"], reverse=True)[:2]
        if dominant_sectors and dominant_sectors[0][1]["total_weight"] > 50:
            insights.append({
                "type": "sector_concentration",
                "severity": "medium",
                "title": f"Sector Concentration: {dominant_sectors[0][0]}",
                "message": f"{len(dominant_sectors[0][1]['stocks'])} overlapping stocks from {dominant_sectors[0][0]} sector.",
                "recommendation": "Your portfolio is heavily concentrated in this sector. Consider diversification."
            })
        
        # Diversification level
        overlap_ratio = (len(stock_analysis) / (len(stock_analysis) + len(set([s["stock"] for s in stock_analysis])))) * 100 if stock_analysis else 0
        if overlap_ratio < 30:
            insights.append({
                "type": "diversification",
                "severity": "low",
                "title": "Good Diversification",
                "message": f"Only {len(stock_analysis)} overlapping stocks across {fund_count} funds.",
                "recommendation": "Your portfolio shows good diversification. Maintain this balance."
            })
        
        return insights
    
    def _calculate_diversification_score(self, stock_analysis: List[Dict], fund_count: int) -> int:
        """Calculate diversification score (0-100)"""
        if not stock_analysis:
            return 100
        
        # Factors:
        # 1. Number of overlapping stocks (lower is better)
        # 2. Concentration in few stocks (lower is better)
        # 3. Sector diversity (higher is better)
        
        high_overlap_count = len([s for s in stock_analysis if s["appears_in"] >= fund_count * 0.7])
        overlap_penalty = (high_overlap_count / len(stock_analysis)) * 50
        
        score = max(0, 100 - overlap_penalty)
        return int(score)
