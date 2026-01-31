"""
Fund data ingestion service
Fetches and updates fund holdings data from various sources
"""
import requests
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
import logging

from app.models.fund_holdings import FundMaster, DataUpdateLog
from app.models.market_data import Stock, StockMarketCapHistory, FundHoldingSnapshot, FundClassification

logger = logging.getLogger(__name__)


class MarketCapClassifier:
    """Classify stocks into Large/Mid/Small cap based on market cap"""
    
    # SEBI definitions (updated periodically)
    LARGE_CAP_THRESHOLD = 20000  # Crores
    MID_CAP_THRESHOLD = 5000     # Crores
    
    @staticmethod
    def classify(market_cap_cr: float) -> str:
        """
        Classify market cap into categories
        
        Args:
            market_cap_cr: Market cap in crores
            
        Returns:
            Category: 'Large', 'Mid', 'Small', or 'Micro'
        """
        if market_cap_cr >= MarketCapClassifier.LARGE_CAP_THRESHOLD:
            return 'Large'
        elif market_cap_cr >= MarketCapClassifier.MID_CAP_THRESHOLD:
            return 'Mid'
        elif market_cap_cr >= 500:
            return 'Small'
        else:
            return 'Micro'


class NSEDataFetcher:
    """Fetch stock data from NSE"""
    
    BASE_URL = "https://www.nseindia.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
    
    def get_market_cap_data(self) -> List[Dict]:
        """
        Fetch market cap data for all NSE stocks
        
        Returns:
            List of dicts with symbol, company_name, market_cap
        """
        try:
            # NSE provides market cap data via their API
            # This is a simplified example - actual implementation needs proper NSE API access
            
            # Option 1: Use NSE's equity market data
            url = f"{self.BASE_URL}/api/equity-stockIndices?index=NIFTY%20500"
            
            # First request to get cookies
            self.session.get(self.BASE_URL)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            stocks = []
            
            for stock in data.get('data', []):
                stocks.append({
                    'symbol': stock.get('symbol'),
                    'company_name': stock.get('companyName'),
                    'market_cap': stock.get('totalTradedVolume', 0) * stock.get('lastPrice', 0) / 10000000,  # Rough estimate
                    'sector': stock.get('industry', 'Unknown')
                })
            
            logger.info(f"Fetched market cap data for {len(stocks)} stocks from NSE")
            return stocks
            
        except Exception as e:
            logger.error(f"Error fetching NSE market cap data: {e}")
            return []


class ValueResearchScraper:
    """Scrape fund holdings from ValueResearch Online"""
    
    BASE_URL = "https://www.valueresearchonline.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_fund(self, fund_name: str) -> Optional[str]:
        """
        Search for fund and get its page URL
        
        Args:
            fund_name: Name of the fund
            
        Returns:
            Fund page URL if found
        """
        try:
            search_url = f"{self.BASE_URL}/funds/search/?q={fund_name}"
            response = self.session.get(search_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find first result (simplified)
            fund_link = soup.find('a', {'class': 'fund-name-link'})
            if fund_link:
                return self.BASE_URL + fund_link['href']
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching fund {fund_name}: {e}")
            return None
    
    def get_fund_holdings(self, fund_url: str) -> List[Dict]:
        """
        Get top holdings for a fund
        
        Args:
            fund_url: URL of fund page
            
        Returns:
            List of holdings with stock_name, weight, sector
        """
        try:
            # Navigate to portfolio/holdings tab
            holdings_url = fund_url + '/portfolio-holdings'
            response = self.session.get(holdings_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            holdings = []
            
            # Parse holdings table (structure varies, this is simplified)
            table = soup.find('table', {'class': 'holdings-table'})
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        holdings.append({
                            'stock_name': cols[0].text.strip(),
                            'weight': float(cols[1].text.strip().replace('%', '')),
                            'sector': cols[2].text.strip() if len(cols) > 2 else 'Unknown'
                        })
            
            logger.info(f"Scraped {len(holdings)} holdings from {fund_url}")
            return holdings
            
        except Exception as e:
            logger.error(f"Error scraping holdings from {fund_url}: {e}")
            return []


class FundDataIngestionService:
    """Main service for ingesting and updating fund data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.nse_fetcher = NSEDataFetcher()
        self.vr_scraper = ValueResearchScraper()
    
    def update_stock_market_caps(self) -> int:
        """
        Update market cap data for all stocks
        
        Returns:
            Number of stocks updated
        """
        logger.info("Starting stock market cap update...")
        
        try:
            # Fetch latest market cap data
            market_cap_data = self.nse_fetcher.get_market_cap_data()
            
            if not market_cap_data:
                logger.warning("No market cap data fetched")
                return 0
            
            updated_count = 0
            today = date.today()
            
            for stock_data in market_cap_data:
                symbol = stock_data['symbol']
                market_cap = stock_data['market_cap']
                category = MarketCapClassifier.classify(market_cap)
                
                # Get or create stock
                stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
                
                if not stock:
                    stock = Stock(
                        symbol=symbol,
                        company_name=stock_data['company_name'],
                        sector=stock_data['sector']
                    )
                    self.db.add(stock)
                    self.db.flush()
                
                # Update current market cap
                stock.market_cap = market_cap
                stock.market_cap_category = category
                stock.last_updated = datetime.utcnow()
                
                # Add historical record
                history = StockMarketCapHistory(
                    stock_id=stock.id,
                    market_cap=market_cap,
                    market_cap_category=category,
                    effective_date=today,
                    source='nse'
                )
                self.db.add(history)
                
                updated_count += 1
            
            self.db.commit()
            logger.info(f"Updated market cap for {updated_count} stocks")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating stock market caps: {e}")
            self.db.rollback()
            return 0
    
    def update_fund_holdings(self, fund_id: int, fund_name: str) -> bool:
        """
        Update holdings for a specific fund
        
        Args:
            fund_id: Fund ID in database
            fund_name: Fund name for searching
            
        Returns:
            True if successful
        """
        logger.info(f"Updating holdings for fund: {fund_name}")
        
        try:
            # Search for fund on ValueResearch
            fund_url = self.vr_scraper.search_fund(fund_name)
            
            if not fund_url:
                logger.warning(f"Fund not found: {fund_name}")
                return False
            
            # Get holdings
            holdings = self.vr_scraper.get_fund_holdings(fund_url)
            
            if not holdings:
                logger.warning(f"No holdings found for {fund_name}")
                return False
            
            today = date.today()
            
            # Save holdings snapshot
            for holding in holdings:
                # Try to match stock
                stock = self.db.query(Stock).filter(
                    Stock.company_name.ilike(f"%{holding['stock_name']}%")
                ).first()
                
                snapshot = FundHoldingSnapshot(
                    fund_id=fund_id,
                    stock_symbol=stock.symbol if stock else holding['stock_name'],
                    stock_name=holding['stock_name'],
                    weight=holding['weight'],
                    market_cap=stock.market_cap if stock else None,
                    market_cap_category=stock.market_cap_category if stock else None,
                    sector=holding.get('sector'),
                    as_of_date=today,
                    source='valueresearch'
                )
                self.db.add(snapshot)
            
            # Calculate and save classification
            self._calculate_fund_classification(fund_id, today)
            
            self.db.commit()
            logger.info(f"Successfully updated holdings for {fund_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating fund holdings: {e}")
            self.db.rollback()
            return False
    
    def _calculate_fund_classification(self, fund_id: int, as_of_date: date):
        """Calculate fund classification based on holdings"""
        
        # Get latest holdings
        holdings = self.db.query(FundHoldingSnapshot).filter(
            FundHoldingSnapshot.fund_id == fund_id,
            FundHoldingSnapshot.as_of_date == as_of_date
        ).all()
        
        if not holdings:
            return
        
        # Calculate allocations
        large_cap_weight = sum(h.weight for h in holdings if h.market_cap_category == 'Large')
        mid_cap_weight = sum(h.weight for h in holdings if h.market_cap_category == 'Mid')
        small_cap_weight = sum(h.weight for h in holdings if h.market_cap_category == 'Small')
        
        # Calculate sector concentrations
        sector_weights = {}
        for h in holdings:
            if h.sector:
                sector_weights[h.sector] = sector_weights.get(h.sector, 0) + h.weight
        
        top_sectors = sorted(sector_weights.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Create classification record
        classification = FundClassification(
            fund_id=fund_id,
            large_cap_percentage=large_cap_weight,
            mid_cap_percentage=mid_cap_weight,
            small_cap_percentage=small_cap_weight,
            top_sector_1=top_sectors[0][0] if len(top_sectors) > 0 else None,
            top_sector_1_weight=top_sectors[0][1] if len(top_sectors) > 0 else None,
            top_sector_2=top_sectors[1][0] if len(top_sectors) > 1 else None,
            top_sector_2_weight=top_sectors[1][1] if len(top_sectors) > 1 else None,
            top_sector_3=top_sectors[2][0] if len(top_sectors) > 2 else None,
            top_sector_3_weight=top_sectors[2][1] if len(top_sectors) > 2 else None,
            number_of_stocks=len(holdings),
            as_of_date=as_of_date
        )
        
        self.db.add(classification)
    
    def run_weekly_update(self) -> Dict:
        """
        Run weekly data update job
        
        Returns:
            Update statistics
        """
        start_time = datetime.utcnow()
        
        logger.info("Starting weekly fund data update...")
        
        # Step 1: Update stock market caps
        stocks_updated = self.update_stock_market_caps()
        
        # Step 2: Update fund holdings (batch process)
        funds = self.db.query(FundMaster).all()
        funds_updated = 0
        funds_failed = 0
        
        for fund in funds:
            try:
                if self.update_fund_holdings(fund.id, fund.fund_name):
                    funds_updated += 1
                else:
                    funds_failed += 1
            except Exception as e:
                logger.error(f"Error updating fund {fund.fund_name}: {e}")
                funds_failed += 1
        
        # Log the update
        end_time = datetime.utcnow()
        
        log = DataUpdateLog(
            update_type='weekly',
            source='automated',
            funds_updated=funds_updated,
            status='success' if funds_failed == 0 else 'partial',
            started_at=start_time,
            completed_at=end_time,
            update_metadata={
                'stocks_updated': stocks_updated,
                'funds_attempted': len(funds),
                'funds_succeeded': funds_updated,
                'funds_failed': funds_failed
            }
        )
        self.db.add(log)
        self.db.commit()
        
        logger.info(f"Weekly update completed. Stocks: {stocks_updated}, Funds: {funds_updated}/{len(funds)}")
        
        return {
            'stocks_updated': stocks_updated,
            'funds_updated': funds_updated,
            'funds_failed': funds_failed,
            'duration_seconds': (end_time - start_time).total_seconds()
        }
