"""
Asset Class Classifier Service

Classifies mutual funds into asset classes: Equity, Debt, Hybrid, Commodity, Other
"""

from typing import Optional


class AssetClassifier:
    """Classifies mutual funds by asset class"""
    
    # Debt fund categories
    DEBT_CATEGORIES = {
        'Liquid', 'Ultra Short Duration', 'Short Duration', 'Low Duration',
        'Money Market', 'Corporate Bond', 'Banking & PSU', 'Gilt',
        'Dynamic Bond', 'Credit Risk', 'Floater', 'Medium Duration',
        'Medium to Long Duration', 'Long Duration', 'Debt', 'Fixed Income'
    }
    
    # Hybrid fund categories
    HYBRID_CATEGORIES = {
        'Hybrid', 'Balanced', 'Conservative Hybrid', 'Aggressive Hybrid',
        'Dynamic Asset Allocation', 'Multi Asset Allocation',
        'Arbitrage', 'Equity Savings', 'Balanced Advantage'
    }
    
    # Equity fund categories (default)
    EQUITY_CATEGORIES = {
        'Large Cap', 'Mid Cap', 'Small Cap', 'Flexi Cap', 'Multi Cap',
        'Large & Mid Cap', 'Focused', 'ELSS', 'Value', 'Contra',
        'Sectoral', 'Thematic', 'International', 'Index', 'ETF'
    }
    
    # Commodity-related keywords
    COMMODITY_KEYWORDS = [
        'gold', 'silver', 'commodity', 'metal', 'precious',
        'bullion', 'gold etf', 'silver etf'
    ]
    
    @staticmethod
    def classify(
        category: Optional[str],
        fund_name: Optional[str],
        fund_type: Optional[str] = None
    ) -> str:
        """
        Classify fund into asset class.
        
        Args:
            category: Fund category (e.g., "Large Cap", "Liquid", "Hybrid")
            fund_name: Full fund name
            fund_type: Optional type from CAS (EQUITY, DEBT, etc.)
            
        Returns:
            Asset class: 'Equity', 'Debt', 'Hybrid', 'Commodity', or 'Other'
        """
        # Normalize inputs
        category = (category or '').strip()
        fund_name = (fund_name or '').strip().lower()
        fund_type = (fund_type or '').strip().upper()
        
        # Check commodity first (most specific)
        if AssetClassifier._is_commodity(fund_name):
            return 'Commodity'
        
        # Check category (most reliable)
        if category in AssetClassifier.DEBT_CATEGORIES:
            return 'Debt'
        
        if category in AssetClassifier.HYBRID_CATEGORIES:
            return 'Hybrid'
        
        if category in AssetClassifier.EQUITY_CATEGORIES:
            return 'Equity'
        
        # Check fund_type from CAS
        if fund_type == 'DEBT':
            return 'Debt'
        
        # Check fund name for keywords (fallback)
        if any(keyword in fund_name for keyword in ['liquid', 'debt', 'bond', 'gilt', 'duration', 'credit']):
            return 'Debt'
        
        if any(keyword in fund_name for keyword in ['hybrid', 'balanced', 'arbitrage', 'allocation']):
            return 'Hybrid'
        
        # Default to Equity (most common)
        return 'Equity'
    
    @staticmethod
    def _is_commodity(fund_name: str) -> bool:
        """Check if fund is commodity-based"""
        return any(keyword in fund_name for keyword in AssetClassifier.COMMODITY_KEYWORDS)
    
    @staticmethod
    def get_asset_class_color(asset_class: str) -> str:
        """Get color code for asset class visualization"""
        colors = {
            'Equity': '#7FC04C',      # Green
            'Debt': '#3B82F6',        # Blue
            'Hybrid': '#F59E0B',      # Orange
            'Commodity': '#EAB308',   # Yellow
            'Other': '#6B7280'        # Gray
        }
        return colors.get(asset_class, colors['Other'])
    
    @staticmethod
    def get_asset_class_icon(asset_class: str) -> str:
        """Get emoji icon for asset class"""
        icons = {
            'Equity': '📈',
            'Debt': '🏦',
            'Hybrid': '⚖️',
            'Commodity': '🥇',
            'Other': '📊'
        }
        return icons.get(asset_class, icons['Other'])
    
    @staticmethod
    def get_risk_profile(asset_class: str) -> str:
        """Get typical risk profile for asset class"""
        profiles = {
            'Equity': 'High',
            'Debt': 'Low',
            'Hybrid': 'Moderate',
            'Commodity': 'High',
            'Other': 'Unknown'
        }
        return profiles.get(asset_class, profiles['Other'])
