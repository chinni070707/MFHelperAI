"""
Production-ready JSON loader with caching and validation
Use this in your FastAPI app to load fund holdings efficiently
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class FundHoldingsLoader:
    """
    Singleton loader for fund holdings with caching and validation
    """
    _instance = None
    _cache: Optional[Dict] = None
    _cache_time: Optional[datetime] = None
    _cache_ttl = timedelta(hours=1)  # Cache for 1 hour
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / 'data' / 'fund_holdings.json'
    
    def load(self, force_reload: bool = False) -> Dict:
        """
        Load fund holdings with caching
        
        Args:
            force_reload: Force reload from disk (bypass cache)
        
        Returns:
            Dict with fund holdings data
        """
        # Check cache validity
        if not force_reload and self._is_cache_valid():
            logger.info("Returning cached fund holdings")
            return self._cache
        
        # Load from disk
        try:
            logger.info(f"Loading fund holdings from {self.data_file}")
            
            with open(self.data_file, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
            
            # Validate structure
            if 'funds' not in data:
                raise ValueError("Invalid fund_holdings.json: missing 'funds' key")
            
            fund_count = len(data['funds'])
            logger.info(f"Loaded {fund_count} funds successfully")
            
            # Validate data quality
            self._validate_data(data)
            
            # Update cache
            self._cache = data
            self._cache_time = datetime.now()
            
            return data
            
        except FileNotFoundError:
            logger.error(f"Fund holdings file not found: {self.data_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in fund holdings: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading fund holdings: {e}")
            raise
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if self._cache is None or self._cache_time is None:
            return False
        
        age = datetime.now() - self._cache_time
        return age < self._cache_ttl
    
    def _validate_data(self, data: Dict) -> None:
        """
        Validate fund holdings data quality
        
        Raises:
            ValueError: If data quality is insufficient
        """
        funds = data.get('funds', {})
        
        if len(funds) < 50:
            logger.warning(f"Low fund count: {len(funds)} (expected >50)")
        
        # Check sample fund for required fields
        if funds:
            sample_key = next(iter(funds))
            sample_fund = funds[sample_key]
            
            required_fields = ['name', 'holdings']
            missing = [f for f in required_fields if f not in sample_fund]
            
            if missing:
                raise ValueError(f"Invalid fund structure: missing {missing}")
            
            # Check holdings have weight
            if sample_fund['holdings'] and 'weight' not in sample_fund['holdings'][0]:
                raise ValueError("Invalid holdings structure: missing 'weight'")
        
        logger.info("Fund holdings data validation passed")
    
    def get_fund_by_key(self, fund_key: str) -> Optional[Dict]:
        """
        Get a specific fund by key
        
        Args:
            fund_key: Fund identifier key
        
        Returns:
            Fund data or None if not found
        """
        data = self.load()
        return data['funds'].get(fund_key)
    
    def get_all_fund_names(self) -> Dict[str, str]:
        """
        Get mapping of fund_key -> fund_name
        
        Returns:
            Dict mapping fund keys to display names
        """
        data = self.load()
        return {
            key: fund['name'] 
            for key, fund in data['funds'].items()
        }
    
    def get_fund_count(self) -> int:
        """Get total number of funds"""
        data = self.load()
        return len(data['funds'])
    
    def clear_cache(self):
        """Clear the cache (for testing or forced reload)"""
        self._cache = None
        self._cache_time = None
        logger.info("Fund holdings cache cleared")


# Singleton instance
fund_loader = FundHoldingsLoader()


# Example usage in FastAPI
"""
from app.utils.fund_loader import fund_loader

@app.get("/api/funds")
async def get_funds():
    data = fund_loader.load()
    return {"funds": list(data['funds'].keys())}

@app.get("/api/funds/{fund_key}")
async def get_fund(fund_key: str):
    fund = fund_loader.get_fund_by_key(fund_key)
    if not fund:
        raise HTTPException(404, "Fund not found")
    return fund

# Force reload after scraping new data
@app.post("/api/admin/reload-funds")
async def reload_funds():
    fund_loader.load(force_reload=True)
    return {"status": "reloaded", "count": fund_loader.get_fund_count()}
"""
