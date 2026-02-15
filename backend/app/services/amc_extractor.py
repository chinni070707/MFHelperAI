"""
AMC Name Extractor Service
Extracts and validates Asset Management Company names from fund names.
"""

from typing import Set

class AmcExtractor:
    """Service for extracting and validating AMC names from mutual fund names."""
    
    # Known AMC patterns - maps keywords to official AMC names
    AMC_KEYWORDS = {
        'HDFC': 'HDFC Mutual Fund',
        'ICICI': 'ICICI Prudential Mutual Fund',
        'SBI': 'SBI Mutual Fund',
        'Axis': 'Axis Mutual Fund',
        'Kotak': 'Kotak Mahindra Mutual Fund',
        'Aditya Birla': 'Aditya Birla Sun Life Mutual Fund',
        'Nippon': 'Nippon India Mutual Fund',
        'UTI': 'UTI Mutual Fund',
        'DSP': 'DSP Mutual Fund',
        'Franklin': 'Franklin Templeton Mutual Fund',
        'Mirae': 'Mirae Asset Mutual Fund',
        'Parag Parikh': 'PPFAS Mutual Fund',
        'PPFAS': 'PPFAS Mutual Fund',
        'Motilal Oswal': 'Motilal Oswal Mutual Fund',
        'Edelweiss': 'Edelweiss Mutual Fund',
        'PGIM': 'PGIM India Mutual Fund',
        'Tata': 'Tata Mutual Fund',
        'Invesco': 'Invesco Mutual Fund',
        'Sundaram': 'Sundaram Mutual Fund',
        'Quantum': 'Quantum Mutual Fund',
        'Quant': 'Quant Mutual Fund',
        'Mahindra': 'Mahindra Manulife Mutual Fund',
        'HSBC': 'HSBC Mutual Fund',
        'Baroda': 'Baroda BNP Paribas Mutual Fund',
        'LIC': 'LIC Mutual Fund',
        'Canara Robeco': 'Canara Robeco Mutual Fund',
        'BOI AXA': 'BOI AXA Mutual Fund',
        'JM Financial': 'JM Financial Mutual Fund',
        'IDFC': 'IDFC Mutual Fund',
        'L&T': 'L&T Mutual Fund',
        'Principal': 'Principal Mutual Fund',
        'Shriram': 'Shriram Mutual Fund',
        'Bajaj': 'Bajaj Finserv Mutual Fund',
        'WhiteOak': 'WhiteOak Capital Mutual Fund',
        'Groww': 'Groww Mutual Fund',
        'Samco': 'Samco Mutual Fund',
        'Union': 'Union Mutual Fund',
        'ITI': 'ITI Mutual Fund',
        'Navi': 'Navi Mutual Fund',
        'NJ': 'NJ Mutual Fund',
        'Trust': 'Trust Mutual Fund',
        '360 ONE': '360 ONE Mutual Fund',
        'Helios': 'Helios Mutual Fund',
    }
    
    # Invalid terms that should never be AMC names
    INVALID_AMC_TERMS = {
        'Tax', 'Cap', 'Equity', 'Debt', 'Hybrid', 'ELSS', 'Index', 
        'Midcap', 'Smallcap', 'Largecap', 'Multicap', 'Flexi',
        'Growth', 'Value', 'Dividend', 'Direct', 'Regular',
        'Fund', 'Mutual', 'Savings', 'Income', 'Liquid',
        'Term', 'Short', 'Long', 'Ultra', 'Dynamic',
        'Focused', 'Balanced', 'Conservative', 'Aggressive',
    }
    
    @classmethod
    def extract(cls, fund_name: str) -> str:
        """
        Extract AMC name from fund name using keyword matching.
        
        Args:
            fund_name: Full mutual fund name (e.g., "Axis Long Term Equity Fund")
            
        Returns:
            Standardized AMC name (e.g., "Axis Mutual Fund")
            
        Examples:
            >>> AmcExtractor.extract("Axis Long Term Equity Fund")
            "Axis Mutual Fund"
            >>> AmcExtractor.extract("HDFC Tax Saver ELSS Direct Plan")
            "HDFC Mutual Fund"
            >>> AmcExtractor.extract("Parag Parikh Flexi Cap Fund")
            "PPFAS Mutual Fund"
        """
        if not fund_name:
            return "Unknown"
        
        # Keyword matching - check longest matches first (for "Aditya Birla", "Parag Parikh", etc.)
        sorted_keywords = sorted(cls.AMC_KEYWORDS.keys(), key=len, reverse=True)
        
        for keyword in sorted_keywords:
            if keyword.lower() in fund_name.lower():
                return cls.AMC_KEYWORDS[keyword]
        
        # Fallback: Extract first word + "Mutual Fund"
        first_word = fund_name.split()[0] if fund_name.split() else "Unknown"
        
        # Don't use invalid terms as AMC names
        if first_word in cls.INVALID_AMC_TERMS:
            return "Unknown"
        
        return f"{first_word} Mutual Fund"
    
    @classmethod
    def is_valid(cls, amc_name: str) -> bool:
        """
        Check if AMC name is valid (not a fund category/type term).
        
        Args:
            amc_name: AMC name to validate
            
        Returns:
            True if valid AMC name, False if it's a category/type term
        """
        if not amc_name or amc_name == "Unknown":
            return False
        
        # Check if it's an invalid term
        for invalid_term in cls.INVALID_AMC_TERMS:
            if invalid_term.lower() == amc_name.lower():
                return False
        
        return True
    
    @classmethod
    def get_all_known_amcs(cls) -> Set[str]:
        """Get set of all known AMC names."""
        return set(cls.AMC_KEYWORDS.values())
    
    @classmethod
    def normalize(cls, amc_name: str) -> str:
        """
        Normalize AMC name to standard format.
        
        Args:
            amc_name: AMC name to normalize (e.g., "HDFC", "hdfc", "HDFC AMC")
            
        Returns:
            Standardized AMC name (e.g., "HDFC Mutual Fund")
        """
        if not amc_name:
            return "Unknown"
        
        # Check if already a known AMC name
        if amc_name in cls.AMC_KEYWORDS.values():
            return amc_name
        
        # Try to extract from the name
        return cls.extract(amc_name)
