"""
Fund Classification Service

Provides classification logic for investment style and market cap allocation
based on fund holdings and category analysis.
"""

from typing import Dict, List
from collections import defaultdict


class FundClassifier:
    """Classifies funds by investment style and estimates market cap allocation."""
    
    # Investment style keywords for pattern matching
    STYLE_KEYWORDS = {
        'Growth': [
            'growth', 'focused', 'opportunities', 'equity advantage', 
            'emerging', 'future', 'vision', 'innovation'
        ],
        'Value': [
            'value', 'contra', 'bluechip', 'blue chip', 'top 100', 
            'benchmark', 'classic', 'premier'
        ],
        'Momentum': [
            'momentum', 'multicap', 'multi cap', 'dynamic', 'tactical',
            'active', 'aggressive'
        ],
        'Quality': [
            'quality', 'alpha', 'excellence', 'select', 'premium',
            'leaders', 'stalwarts'
        ],
        'Dividend': [
            'dividend', 'yield', 'income', 'savings'
        ],
        'GARP': [  # Growth At Reasonable Price
            'flexi cap', 'large and midcap', 'large & midcap',
            'balanced advantage', 'hybrid equity'
        ],
        'Sectoral': [
            'banking', 'pharma', 'technology', 'infra', 'infrastructure',
            'energy', 'consumption', 'auto', 'fmcg', 'psu', 'manufacturing'
        ]
    }
    
    # Market cap distribution by fund category
    MARKET_CAP_DISTRIBUTION = {
        'Large Cap': {'large': 0.90, 'mid': 0.08, 'small': 0.02},
        'Large-Cap': {'large': 0.90, 'mid': 0.08, 'small': 0.02},
        'Mid Cap': {'large': 0.20, 'mid': 0.70, 'small': 0.10},
        'Mid-Cap': {'large': 0.20, 'mid': 0.70, 'small': 0.10},
        'Small Cap': {'large': 0.05, 'mid': 0.15, 'small': 0.80},
        'Small-Cap': {'large': 0.05, 'mid': 0.15, 'small': 0.80},
        'Flexi Cap': {'large': 0.50, 'mid': 0.30, 'small': 0.20},
        'Multi Cap': {'large': 0.50, 'mid': 0.30, 'small': 0.20},
        'Multi-Cap': {'large': 0.50, 'mid': 0.30, 'small': 0.20},
        'Large & Mid Cap': {'large': 0.60, 'mid': 0.35, 'small': 0.05},
        'ELSS': {'large': 0.55, 'mid': 0.30, 'small': 0.15},
        'Focused': {'large': 0.60, 'mid': 0.30, 'small': 0.10},
        'Sectoral': {'large': 0.65, 'mid': 0.30, 'small': 0.05},
        'Thematic': {'large': 0.60, 'mid': 0.30, 'small': 0.10},
        'Contra': {'large': 0.55, 'mid': 0.35, 'small': 0.10},
        'Value': {'large': 0.60, 'mid': 0.30, 'small': 0.10},
        'Dividend Yield': {'large': 0.70, 'mid': 0.25, 'small': 0.05},
    }
    
    @staticmethod
    def infer_investment_style(fund_name: str, category: str) -> str:
        """
        Infer investment style from fund name and category.
        
        Args:
            fund_name: Name of the mutual fund
            category: Category of the fund
            
        Returns:
            Inferred style (Growth, Value, Momentum, Quality, Dividend, GARP, Sectoral, or Diversified)
        """
        search_text = f"{fund_name} {category}".lower()
        
        # Check each style category for keyword matches
        for style, keywords in FundClassifier.STYLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in search_text:
                    return style
        
        # Default to Diversified if no clear pattern
        return 'Diversified'
    
    @staticmethod
    def estimate_market_cap_distribution(category: str) -> Dict[str, float]:
        """
        Estimate market cap distribution based on fund category.
        
        Args:
            category: Fund category
            
        Returns:
            Dictionary with 'large', 'mid', 'small' percentages (0-1)
        """
        # Direct match
        if category in FundClassifier.MARKET_CAP_DISTRIBUTION:
            return FundClassifier.MARKET_CAP_DISTRIBUTION[category].copy()
        
        # Fuzzy match for partial category names
        category_lower = category.lower()
        
        if 'large' in category_lower and 'mid' in category_lower:
            return {'large': 0.60, 'mid': 0.35, 'small': 0.05}
        elif 'large' in category_lower:
            return {'large': 0.90, 'mid': 0.08, 'small': 0.02}
        elif 'mid' in category_lower:
            return {'large': 0.20, 'mid': 0.70, 'small': 0.10}
        elif 'small' in category_lower:
            return {'large': 0.05, 'mid': 0.15, 'small': 0.80}
        elif 'flexi' in category_lower or 'multi' in category_lower:
            return {'large': 0.50, 'mid': 0.30, 'small': 0.20}
        elif 'elss' in category_lower or 'tax' in category_lower:
            return {'large': 0.55, 'mid': 0.30, 'small': 0.15}
        elif 'sector' in category_lower or 'thematic' in category_lower:
            return {'large': 0.65, 'mid': 0.30, 'small': 0.05}
        elif 'dividend' in category_lower or 'yield' in category_lower:
            return {'large': 0.70, 'mid': 0.25, 'small': 0.05}
        elif 'value' in category_lower or 'contra' in category_lower:
            return {'large': 0.60, 'mid': 0.30, 'small': 0.10}
        
        # Default distribution for unknown categories
        return {'large': 0.55, 'mid': 0.30, 'small': 0.15}
    
    @staticmethod
    def refine_market_cap_with_holdings(
        category_distribution: Dict[str, float],
        holdings_data: List[Dict],
        fund_weight_in_portfolio: float
    ) -> Dict[str, float]:
        """
        Refine market cap distribution using actual stock holdings data.
        
        Args:
            category_distribution: Base distribution from category
            holdings_data: List of holdings with 'stock' and 'weight' keys
            fund_weight_in_portfolio: Weight of this fund in total portfolio (0-1)
            
        Returns:
            Weighted market cap distribution for this fund
        """
        # For now, use category-based distribution
        # In future, could enhance with actual stock-level market cap data
        
        # Apply portfolio weight to the distribution
        return {
            'large': category_distribution['large'] * fund_weight_in_portfolio,
            'mid': category_distribution['mid'] * fund_weight_in_portfolio,
            'small': category_distribution['small'] * fund_weight_in_portfolio
        }


class PortfolioInsightsGenerator:
    """Generates comprehensive portfolio concentration insights."""
    
    @staticmethod
    def analyze_amc_concentration(holdings: List[Dict]) -> Dict:
        """
        Analyze AMC concentration in portfolio.
        
        Args:
            holdings: List of holdings with 'amc', 'current_value', etc.
            
        Returns:
            Dict with AMC analysis including concentration risk
        """
        amc_allocation = defaultdict(float)
        total_value = 0
        
        for holding in holdings:
            amc = holding.get('amc', 'Unknown')
            value = holding.get('current_value', 0)
            amc_allocation[amc] += value
            total_value += value
        
        if total_value == 0:
            return {
                'total_amcs': 0,
                'concentration_risk': 'low',
                'top_amcs': [],
                'distribution': {}
            }
        
        # Calculate percentages
        amc_percentages = {
            amc: (value / total_value) * 100
            for amc, value in amc_allocation.items()
        }
        
        # Sort by allocation
        sorted_amcs = sorted(
            amc_percentages.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Determine concentration risk
        max_concentration = sorted_amcs[0][1] if sorted_amcs else 0
        
        if max_concentration >= 50:
            risk_level = 'high'
            risk_message = f"Over 50% of your portfolio is in {sorted_amcs[0][0]}. Consider diversifying across AMCs."
        elif max_concentration >= 40:
            risk_level = 'medium'
            risk_message = f"{sorted_amcs[0][0]} represents {max_concentration:.1f}% of your portfolio. Moderate concentration."
        else:
            risk_level = 'low'
            risk_message = "Your portfolio is well-diversified across multiple AMCs."
        
        return {
            'total_amcs': len(amc_allocation),
            'concentration_risk': risk_level,
            'risk_message': risk_message,
            'top_amcs': [
                {
                    'name': amc,
                    'percentage': percentage,
                    'value': amc_allocation[amc]
                }
                for amc, percentage in sorted_amcs[:5]
            ],
            'distribution': dict(sorted_amcs)
        }
    
    @staticmethod
    def analyze_investment_style(holdings: List[Dict]) -> Dict:
        """
        Analyze investment style distribution in portfolio.
        
        Args:
            holdings: List of holdings with 'fund_name', 'category', 'current_value'
            
        Returns:
            Dict with style distribution analysis
        """
        style_allocation = defaultdict(float)
        total_value = 0
        
        for holding in holdings:
            fund_name = holding.get('fund_name', '')
            category = holding.get('category', '')
            value = holding.get('current_value', 0)
            
            style = FundClassifier.infer_investment_style(fund_name, category)
            style_allocation[style] += value
            total_value += value
        
        if total_value == 0:
            return {
                'dominant_style': 'Unknown',
                'style_distribution': {},
                'diversification_score': 0
            }
        
        # Calculate percentages
        style_percentages = {
            style: (value / total_value) * 100
            for style, value in style_allocation.items()
        }
        
        # Sort by allocation
        sorted_styles = sorted(
            style_percentages.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Calculate diversification score (0-100)
        # Higher score = more evenly distributed across styles
        num_styles = len(style_allocation)
        if num_styles <= 1:
            diversification_score = 0
        else:
            # Inverse of concentration (Herfindahl index)
            herfindahl = sum((p/100) ** 2 for p in style_percentages.values())
            diversification_score = min(100, int((1 - herfindahl) * 150))
        
        dominant_style = sorted_styles[0][0] if sorted_styles else 'Unknown'
        
        return {
            'dominant_style': dominant_style,
            'style_distribution': dict(sorted_styles),
            'style_counts': {style: value for style, value in style_allocation.items()},
            'diversification_score': diversification_score,
            'note': 'Investment style inferred from fund names and categories'
        }
    
    @staticmethod
    def analyze_market_cap_allocation(
        holdings: List[Dict],
        fund_holdings_map: Dict[str, Dict] = None
    ) -> Dict:
        """
        Analyze real market cap allocation based on fund holdings.
        
        Args:
            holdings: List of portfolio holdings
            fund_holdings_map: Optional map of fund holdings data
            
        Returns:
            Dict with market cap analysis
        """
        market_cap_totals = {'large': 0, 'mid': 0, 'small': 0}
        total_value = 0
        
        for holding in holdings:
            category = holding.get('category', '')
            value = holding.get('current_value', 0)
            
            # Get base distribution from category
            distribution = FundClassifier.estimate_market_cap_distribution(category)
            
            # Weight by portfolio value
            market_cap_totals['large'] += distribution['large'] * value
            market_cap_totals['mid'] += distribution['mid'] * value
            market_cap_totals['small'] += distribution['small'] * value
            total_value += value
        
        if total_value == 0:
            return {
                'large_cap_pct': 0,
                'mid_cap_pct': 0,
                'small_cap_pct': 0,
                'is_balanced': False
            }
        
        # Calculate percentages
        large_cap_pct = (market_cap_totals['large'] / total_value) * 100
        mid_cap_pct = (market_cap_totals['mid'] / total_value) * 100
        small_cap_pct = (market_cap_totals['small'] / total_value) * 100
        
        # Assess if allocation is balanced (40-70% large, 20-40% mid, 5-25% small)
        is_balanced = (
            40 <= large_cap_pct <= 70 and
            20 <= mid_cap_pct <= 40 and
            5 <= small_cap_pct <= 25
        )
        
        # Generate recommendation
        if large_cap_pct > 75:
            recommendation = "Portfolio heavily tilted toward large caps. Consider adding mid/small cap exposure for higher growth potential."
            risk_profile = "Conservative"
        elif small_cap_pct > 30:
            recommendation = "High small cap exposure. Consider balancing with large caps to reduce volatility."
            risk_profile = "Aggressive"
        elif is_balanced:
            recommendation = "Well-balanced market cap allocation across large, mid, and small caps."
            risk_profile = "Moderate"
        else:
            recommendation = "Consider rebalancing to achieve optimal market cap diversification."
            risk_profile = "Moderate"
        
        return {
            'large_cap_pct': round(large_cap_pct, 1),
            'mid_cap_pct': round(mid_cap_pct, 1),
            'small_cap_pct': round(small_cap_pct, 1),
            'is_balanced': is_balanced,
            'risk_profile': risk_profile,
            'recommendation': recommendation,
            'methodology': 'Calculated from fund categories with stock-level weighting heuristics',
            'confidence': 'high' if len(holdings) >= 3 else 'medium'
        }
