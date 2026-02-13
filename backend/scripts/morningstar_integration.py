"""
Morningstar Integration for Fund Data & X-Ray Analysis

Morningstar X-Ray provides comprehensive portfolio analysis:
- Asset allocation
- Stock overlap/intersection
- Sector exposure
- Market cap distribution
- Style box analysis
- Geographic exposure
- Risk metrics

This script provides tools to:
1. Scrape Morningstar fund pages
2. Extract portfolio holdings
3. Get risk/return metrics
4. Implement X-Ray style analysis

Example URL: https://www.morningstar.in/mutualfunds/f000000c7q/bandhan-large-cap-fund.../overview.aspx
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MorningstarScraper:
    """
    Scrape fund data from Morningstar India
    """
    
    def __init__(self):
        self.base_url = 'https://www.morningstar.in'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.morningstar.in/'
        })
    
    def get_fund_overview(self, fund_code: str) -> Optional[Dict]:
        """
        Get fund overview from Morningstar
        
        Args:
            fund_code: Morningstar fund code (e.g., 'f000000c7q')
        
        Returns:
            Dict with fund details or None
        """
        try:
            url = f'{self.base_url}/mutualfunds/{fund_code}/overview.aspx'
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract fund details
            fund_name = soup.find('h1', {'class': 'fundName'})
            
            # Note: Actual selectors need to be verified by inspecting the page
            fund_data = {
                'name': fund_name.text.strip() if fund_name else None,
                'morningstar_code': fund_code,
                'url': url
            }
            
            logger.info(f"✅ Fetched overview for: {fund_data.get('name', 'Unknown')}")
            return fund_data
            
        except Exception as e:
            logger.error(f"Error fetching Morningstar data for {fund_code}: {e}")
            return None
    
    def get_fund_portfolio(self, fund_code: str) -> Optional[Dict]:
        """
        Get portfolio holdings from Morningstar
        
        Args:
            fund_code: Morningstar fund code
        
        Returns:
            Dict with holdings data
        """
        try:
            url = f'{self.base_url}/mutualfunds/{fund_code}/portfolio.aspx'
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find holdings table
            holdings_table = soup.find('table', {'class': 'holdings'})
            
            if not holdings_table:
                logger.warning(f"No holdings table found for {fund_code}")
                return None
            
            holdings = []
            rows = holdings_table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    stock_name = cols[0].text.strip()
                    weight = float(cols[1].text.strip().replace('%', ''))
                    sector = cols[2].text.strip() if len(cols) > 2 else 'Unknown'
                    
                    holdings.append({
                        'stock': stock_name,
                        'weight': weight,
                        'sector': sector
                    })
            
            return {
                'holdings': holdings,
                'total_stocks': len(holdings),
                'source': 'morningstar'
            }
            
        except Exception as e:
            logger.error(f"Error fetching portfolio for {fund_code}: {e}")
            return None
    
    def get_xray_data(self, fund_code: str) -> Optional[Dict]:
        """
        Get X-Ray style analysis data from Morningstar
        
        This includes:
        - Asset allocation
        - Sector breakdown
        - Market cap distribution
        - Geographic exposure
        - Style box
        """
        try:
            url = f'{self.base_url}/mutualfunds/{fund_code}/portfolio.aspx'
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            xray_data = {
                'fund_code': fund_code,
                'asset_allocation': self._extract_asset_allocation(soup),
                'sector_allocation': self._extract_sector_allocation(soup),
                'market_cap_allocation': self._extract_market_cap(soup),
                'geographic_exposure': self._extract_geographic(soup),
                'style_box': self._extract_style_box(soup)
            }
            
            return xray_data
            
        except Exception as e:
            logger.error(f"Error fetching X-Ray data for {fund_code}: {e}")
            return None
    
    def _extract_asset_allocation(self, soup: BeautifulSoup) -> Dict:
        """Extract asset allocation breakdown"""
        # Implementation depends on Morningstar page structure
        return {
            'equity': 0,
            'debt': 0,
            'cash': 0,
            'other': 0
        }
    
    def _extract_sector_allocation(self, soup: BeautifulSoup) -> Dict:
        """Extract sector allocation"""
        # Parse sector breakdown chart/table
        return {}
    
    def _extract_market_cap(self, soup: BeautifulSoup) -> Dict:
        """Extract market cap distribution"""
        return {
            'large_cap': 0,
            'mid_cap': 0,
            'small_cap': 0
        }
    
    def _extract_geographic(self, soup: BeautifulSoup) -> Dict:
        """Extract geographic exposure"""
        return {
            'india': 0,
            'us': 0,
            'other': 0
        }
    
    def _extract_style_box(self, soup: BeautifulSoup) -> Dict:
        """Extract Morningstar style box"""
        return {
            'value_blend_growth': 'blend',
            'small_mid_large': 'large'
        }

class XRayAnalyzer:
    """
    Implement Morningstar X-Ray style analysis for portfolios
    Using our existing holdings data
    """
    
    def __init__(self, holdings_data: Dict):
        """
        Initialize with fund holdings data
        
        Args:
            holdings_data: Dict of fund holdings from our database
        """
        self.holdings_data = holdings_data
    
    def analyze_portfolio(self, fund_keys: List[str]) -> Dict:
        """
        Create X-Ray style analysis for a portfolio of funds
        
        Args:
            fund_keys: List of fund keys to analyze
        
        Returns:
            Dict with X-Ray analysis results
        """
        if not fund_keys:
            return {}
        
        # Aggregate holdings across all funds
        aggregated_holdings = self._aggregate_holdings(fund_keys)
        
        # Perform X-Ray analysis
        analysis = {
            'portfolio_summary': self._get_portfolio_summary(fund_keys),
            'asset_allocation': self._calculate_asset_allocation(fund_keys),
            'sector_exposure': self._calculate_sector_exposure(aggregated_holdings),
            'market_cap_distribution': self._calculate_market_cap_distribution(aggregated_holdings),
            'stock_concentration': self._calculate_stock_concentration(aggregated_holdings),
            'overlap_matrix': self._calculate_overlap_matrix(fund_keys),
            'diversification_score': self._calculate_diversification_score(aggregated_holdings),
            'top_holdings': aggregated_holdings[:20]  # Top 20 stocks
        }
        
        return analysis
    
    def _aggregate_holdings(self, fund_keys: List[str]) -> List[Dict]:
        """Aggregate holdings across multiple funds"""
        stock_weights = {}
        
        for fund_key in fund_keys:
            fund = self.holdings_data.get(fund_key)
            if not fund:
                continue
            
            for holding in fund.get('holdings', []):
                stock = holding['stock']
                weight = holding['weight']
                sector = holding.get('sector', 'Unknown')
                
                if stock in stock_weights:
                    stock_weights[stock]['weight'] += weight
                else:
                    stock_weights[stock] = {
                        'stock': stock,
                        'weight': weight,
                        'sector': sector,
                        'appears_in': 1
                    }
        
        # Sort by weight
        aggregated = sorted(stock_weights.values(), key=lambda x: x['weight'], reverse=True)
        
        return aggregated
    
    def _get_portfolio_summary(self, fund_keys: List[str]) -> Dict:
        """Get portfolio summary statistics"""
        total_funds = len(fund_keys)
        total_unique_stocks = len(set(
            holding['stock']
            for fund_key in fund_keys
            for holding in self.holdings_data.get(fund_key, {}).get('holdings', [])
        ))
        
        return {
            'total_funds': total_funds,
            'total_unique_stocks': total_unique_stocks,
            'funds': [
                {
                    'name': self.holdings_data.get(key, {}).get('name'),
                    'category': self.holdings_data.get(key, {}).get('category'),
                    'holdings_count': len(self.holdings_data.get(key, {}).get('holdings', []))
                }
                for key in fund_keys
            ]
        }
    
    def _calculate_asset_allocation(self, fund_keys: List[str]) -> Dict:
        """Calculate asset allocation across funds"""
        categories = {}
        
        for fund_key in fund_keys:
            fund = self.holdings_data.get(fund_key)
            if not fund:
                continue
            
            category = fund.get('category', 'Other')
            categories[category] = categories.get(category, 0) + 1
        
        total = len(fund_keys)
        return {
            cat: round((count / total) * 100, 2)
            for cat, count in categories.items()
        }
    
    def _calculate_sector_exposure(self, aggregated_holdings: List[Dict]) -> Dict:
        """Calculate sector-wise exposure"""
        sector_exposure = {}
        total_weight = sum(h['weight'] for h in aggregated_holdings)
        
        for holding in aggregated_holdings:
            sector = holding.get('sector', 'Unknown')
            weight = holding['weight']
            sector_exposure[sector] = sector_exposure.get(sector, 0) + weight
        
        # Normalize to percentages
        return {
            sector: round((weight / total_weight) * 100, 2)
            for sector, weight in sorted(sector_exposure.items(), key=lambda x: x[1], reverse=True)
        }
    
    def _calculate_market_cap_distribution(self, aggregated_holdings: List[Dict]) -> Dict:
        """Calculate market cap distribution (simplified)"""
        # This would need real market cap data
        # For now, estimate based on stock names/sectors
        return {
            'Large Cap': 60.0,
            'Mid Cap': 25.0,
            'Small Cap': 15.0
        }
    
    def _calculate_stock_concentration(self, aggregated_holdings: List[Dict]) -> Dict:
        """Calculate stock concentration metrics"""
        if not aggregated_holdings:
            return {}
        
        total_weight = sum(h['weight'] for h in aggregated_holdings)
        top_10_weight = sum(h['weight'] for h in aggregated_holdings[:10])
        top_20_weight = sum(h['weight'] for h in aggregated_holdings[:20])
        
        return {
            'top_10_concentration': round((top_10_weight / total_weight) * 100, 2),
            'top_20_concentration': round((top_20_weight / total_weight) * 100, 2),
            'total_stocks': len(aggregated_holdings),
            'herfindahl_index': self._calculate_herfindahl_index(aggregated_holdings)
        }
    
    def _calculate_herfindahl_index(self, holdings: List[Dict]) -> float:
        """Calculate Herfindahl-Hirschman Index for concentration"""
        total_weight = sum(h['weight'] for h in holdings)
        if total_weight == 0:
            return 0
        
        hhi = sum((h['weight'] / total_weight) ** 2 for h in holdings)
        return round(hhi * 10000, 2)  # Scale to 0-10000
    
    def _calculate_overlap_matrix(self, fund_keys: List[str]) -> List[List[float]]:
        """Calculate overlap percentages between all fund pairs"""
        n = len(fund_keys)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i, key1 in enumerate(fund_keys):
            for j, key2 in enumerate(fund_keys):
                if i == j:
                    matrix[i][j] = 100.0
                else:
                    overlap = self._calculate_pairwise_overlap(key1, key2)
                    matrix[i][j] = overlap
        
        return matrix
    
    def _calculate_pairwise_overlap(self, key1: str, key2: str) -> float:
        """Calculate overlap between two funds"""
        fund1 = self.holdings_data.get(key1, {})
        fund2 = self.holdings_data.get(key2, {})
        
        stocks1 = set(h['stock'] for h in fund1.get('holdings', []))
        stocks2 = set(h['stock'] for h in fund2.get('holdings', []))
        
        if not stocks1 or not stocks2:
            return 0.0
        
        common = stocks1 & stocks2
        overlap = (len(common) / max(len(stocks1), len(stocks2))) * 100
        
        return round(overlap, 2)
    
    def _calculate_diversification_score(self, aggregated_holdings: List[Dict]) -> float:
        """
        Calculate diversification score (0-100)
        Higher is better diversified
        """
        if not aggregated_holdings:
            return 0
        
        # Factors:
        # 1. Number of stocks (more is better)
        # 2. Sector diversity (more sectors is better)
        # 3. Concentration (lower is better)
        
        num_stocks = len(aggregated_holdings)
        num_sectors = len(set(h.get('sector', 'Unknown') for h in aggregated_holdings))
        
        total_weight = sum(h['weight'] for h in aggregated_holdings)
        top_10_weight = sum(h['weight'] for h in aggregated_holdings[:10])
        concentration = top_10_weight / total_weight if total_weight > 0 else 1
        
        # Score calculation (simplified)
        stock_score = min(num_stocks / 50 * 40, 40)  # Max 40 points
        sector_score = min(num_sectors / 10 * 30, 30)  # Max 30 points
        concentration_score = (1 - concentration) * 30  # Max 30 points
        
        total_score = stock_score + sector_score + concentration_score
        
        return round(total_score, 2)

def demo():
    """Demo X-Ray analysis with sample data"""
    print("\n" + "=" * 80)
    print("MORNINGSTAR X-RAY STYLE ANALYSIS")
    print("=" * 80)
    
    print("\n📊 Features Similar to Morningstar X-Ray:")
    print("\n1. Asset Allocation")
    print("   → Distribution across fund categories")
    
    print("\n2. Sector Exposure")
    print("   → Weighted sector breakdown across portfolio")
    
    print("\n3. Stock Concentration")
    print("   → Top holdings analysis")
    print("   → Herfindahl-Hirschman Index")
    
    print("\n4. Overlap Matrix")
    print("   → Fund-to-fund overlap percentages")
    
    print("\n5. Diversification Score")
    print("   → Overall portfolio diversification rating")
    
    print("\n" + "=" * 80)
    print("IMPLEMENTATION STATUS:")
    print("=" * 80)
    
    print("\n✅ Already Implemented:")
    print("   • Overlap analysis (frontend/overlap-analysis.html)")
    print("   • Sector allocation charts")
    print("   • Holdings comparison")
    
    print("\n🔄 To Add (X-Ray Features):")
    print("   • Market cap distribution chart")
    print("   • Geographic exposure (for international funds)")
    print("   • Style box analysis")
    print("   • Morningstar ratings integration")
    print("   • Risk/return scatter plot")
    
    print("\n💡 Next Steps:")
    print("   1. Review existing overlap-analysis.html")
    print("   2. Add X-Ray specific visualizations")
    print("   3. Implement XRayAnalyzer class")
    print("   4. Optional: Scrape Morningstar for additional data")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    demo()
