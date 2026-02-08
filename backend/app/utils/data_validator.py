"""
Data Validation Utilities
Sanity checks for mutual fund master data integrity
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import Dict, List, Any
import logging

from app.models.models import FundMaster

logger = logging.getLogger(__name__)


class FundDataValidator:
    """Validates mutual fund master data integrity"""
    
    def __init__(self, db: Session):
        self.db = db
        self.validation_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks"""
        logger.info("Starting fund data validation...")
        
        # Run all validation checks
        self.check_data_exists()
        self.check_amc_data()
        self.check_fund_completeness()
        self.check_duplicate_funds()
        self.check_invalid_data()
        self.check_data_freshness()
        
        # Calculate summary
        results = {
            "status": "pass" if len(self.validation_results["failed"]) == 0 else "fail",
            "total_checks": len(self.validation_results["passed"]) + len(self.validation_results["failed"]),
            "passed": len(self.validation_results["passed"]),
            "failed": len(self.validation_results["failed"]),
            "warnings": len(self.validation_results["warnings"]),
            "details": self.validation_results
        }
        
        logger.info(f"Validation complete: {results['passed']}/{results['total_checks']} passed")
        return results
    
    def check_data_exists(self):
        """Check if fund master data exists"""
        try:
            total_funds = self.db.query(func.count(FundMaster.id)).scalar()
            
            if total_funds == 0:
                self.validation_results["failed"].append({
                    "check": "data_exists",
                    "message": "No fund data found in database",
                    "severity": "critical"
                })
            elif total_funds < 100:
                self.validation_results["warnings"].append({
                    "check": "data_exists",
                    "message": f"Only {total_funds} funds found - dataset may be incomplete",
                    "severity": "warning"
                })
                self.validation_results["passed"].append({
                    "check": "data_exists",
                    "message": f"Found {total_funds} funds in database"
                })
            else:
                self.validation_results["passed"].append({
                    "check": "data_exists",
                    "message": f"Found {total_funds} funds in database"
                })
        except Exception as e:
            self.validation_results["failed"].append({
                "check": "data_exists",
                "message": f"Error checking data existence: {str(e)}",
                "severity": "critical"
            })
    
    def check_amc_data(self):
        """Validate AMC (Asset Management Company) data"""
        try:
            # Get unique AMCs
            amc_list = self.db.query(distinct(FundMaster.amc)).filter(
                FundMaster.is_active == True
            ).all()
            amc_names = [amc[0] for amc in amc_list if amc[0]]
            
            if len(amc_names) == 0:
                self.validation_results["failed"].append({
                    "check": "amc_data",
                    "message": "No AMCs found in database",
                    "severity": "critical"
                })
                return
            
            # Check for null AMCs
            null_amc_count = self.db.query(func.count(FundMaster.id)).filter(
                FundMaster.amc == None,
                FundMaster.is_active == True
            ).scalar()
            
            if null_amc_count > 0:
                self.validation_results["warnings"].append({
                    "check": "amc_data",
                    "message": f"{null_amc_count} funds have null/missing AMC",
                    "severity": "warning"
                })
            
            # Check for suspiciously short or invalid AMC names
            invalid_amcs = []
            for amc in amc_names:
                if len(amc) < 3:
                    invalid_amcs.append(amc)
            
            if invalid_amcs:
                self.validation_results["warnings"].append({
                    "check": "amc_data",
                    "message": f"Found {len(invalid_amcs)} AMCs with suspiciously short names: {invalid_amcs[:5]}",
                    "severity": "warning"
                })
            
            # Success
            self.validation_results["passed"].append({
                "check": "amc_data",
                "message": f"Found {len(amc_names)} valid AMCs"
            })
            
        except Exception as e:
            self.validation_results["failed"].append({
                "check": "amc_data",
                "message": f"Error validating AMC data: {str(e)}",
                "severity": "error"
            })
    
    def check_fund_completeness(self):
        """Check if each AMC has funds and funds have complete data"""
        try:
            # Get AMCs and their fund counts
            amc_fund_counts = self.db.query(
                FundMaster.amc,
                func.count(FundMaster.id)
            ).filter(
                FundMaster.is_active == True,
                FundMaster.amc != None
            ).group_by(FundMaster.amc).all()
            
            # Check for AMCs with very few funds (might be data quality issue)
            low_fund_amcs = []
            for amc, count in amc_fund_counts:
                if count < 3:
                    low_fund_amcs.append((amc, count))
            
            if low_fund_amcs:
                self.validation_results["warnings"].append({
                    "check": "fund_completeness",
                    "message": f"{len(low_fund_amcs)} AMCs have fewer than 3 funds (might be incomplete)",
                    "data": low_fund_amcs[:10],
                    "severity": "warning"
                })
            
            # Check for funds with missing critical fields
            incomplete_funds = self.db.query(func.count(FundMaster.id)).filter(
                FundMaster.is_active == True,
                or_(
                    FundMaster.scheme_code == None,
                    FundMaster.scheme_name == None,
                    FundMaster.amc == None
                )
            ).scalar()
            
            if incomplete_funds > 0:
                self.validation_results["failed"].append({
                    "check": "fund_completeness",
                    "message": f"{incomplete_funds} funds have missing critical fields (scheme_code, scheme_name, or amc)",
                    "severity": "error"
                })
            else:
                self.validation_results["passed"].append({
                    "check": "fund_completeness",
                    "message": "All active funds have complete critical fields"
                })
                
        except Exception as e:
            self.validation_results["failed"].append({
                "check": "fund_completeness",
                "message": f"Error checking fund completeness: {str(e)}",
                "severity": "error"
            })
    
    def check_duplicate_funds(self):
        """Check for duplicate funds by scheme_code or ISIN"""
        try:
            # Check duplicate scheme codes
            duplicate_codes = self.db.query(
                FundMaster.scheme_code,
                func.count(FundMaster.id)
            ).filter(
                FundMaster.scheme_code != None
            ).group_by(
                FundMaster.scheme_code
            ).having(
                func.count(FundMaster.id) > 1
            ).all()
            
            if duplicate_codes:
                self.validation_results["failed"].append({
                    "check": "duplicate_funds",
                    "message": f"Found {len(duplicate_codes)} duplicate scheme codes",
                    "data": duplicate_codes[:5],
                    "severity": "error"
                })
            else:
                self.validation_results["passed"].append({
                    "check": "duplicate_funds",
                    "message": "No duplicate scheme codes found"
                })
            
            # Check duplicate ISINs
            duplicate_isins = self.db.query(
                FundMaster.isin,
                func.count(FundMaster.id)
            ).filter(
                FundMaster.isin != None
            ).group_by(
                FundMaster.isin
            ).having(
                func.count(FundMaster.id) > 1
            ).all()
            
            if duplicate_isins:
                self.validation_results["warnings"].append({
                    "check": "duplicate_funds",
                    "message": f"Found {len(duplicate_isins)} duplicate ISINs (may be growth/dividend variants)",
                    "data": duplicate_isins[:5],
                    "severity": "warning"
                })
            else:
                self.validation_results["passed"].append({
                    "check": "duplicate_isins",
                    "message": "No duplicate ISINs found"
                })
                
        except Exception as e:
            self.validation_results["failed"].append({
                "check": "duplicate_funds",
                "message": f"Error checking duplicates: {str(e)}",
                "severity": "error"
            })
    
    def check_invalid_data(self):
        """Check for invalid or suspicious data values"""
        try:
            # Check for negative NAV values
            negative_nav = self.db.query(func.count(FundMaster.id)).filter(
                FundMaster.current_nav < 0
            ).scalar()
            
            if negative_nav > 0:
                self.validation_results["failed"].append({
                    "check": "invalid_data",
                    "message": f"{negative_nav} funds have negative NAV",
                    "severity": "error"
                })
            
            # Check for unreasonably high expense ratios (> 5%)
            high_expense = self.db.query(func.count(FundMaster.id)).filter(
                FundMaster.expense_ratio > 5.0
            ).scalar()
            
            if high_expense > 0:
                self.validation_results["warnings"].append({
                    "check": "invalid_data",
                    "message": f"{high_expense} funds have expense ratio > 5%",
                    "severity": "warning"
                })
            
            # Check for unrealistic returns (> 500% or < -100%)
            unrealistic_returns = self.db.query(func.count(FundMaster.id)).filter(
                or_(
                    FundMaster.one_year_return > 500,
                    FundMaster.one_year_return < -100,
                    FundMaster.three_year_return > 500,
                    FundMaster.five_year_return > 500
                )
            ).scalar()
            
            if unrealistic_returns > 0:
                self.validation_results["warnings"].append({
                    "check": "invalid_data",
                    "message": f"{unrealistic_returns} funds have unrealistic return values",
                    "severity": "warning"
                })
            
            if negative_nav == 0 and high_expense == 0 and unrealistic_returns == 0:
                self.validation_results["passed"].append({
                    "check": "invalid_data",
                    "message": "No obviously invalid data values found"
                })
                
        except Exception as e:
            self.validation_results["failed"].append({
                "check": "invalid_data",
                "message": f"Error checking invalid data: {str(e)}",
                "severity": "error"
            })
    
    def check_data_freshness(self):
        """Check if data has been updated recently"""
        try:
            from datetime import datetime, timedelta
            
            # Get most recent update timestamp
            latest_update = self.db.query(func.max(FundMaster.updated_at)).scalar()
            
            if latest_update is None:
                self.validation_results["warnings"].append({
                    "check": "data_freshness",
                    "message": "No update timestamp found",
                    "severity": "warning"
                })
                return
            
            # Check if data is stale (older than 7 days)
            days_old = (datetime.now() - latest_update).days
            
            if days_old > 7:
                self.validation_results["warnings"].append({
                    "check": "data_freshness",
                    "message": f"Data is {days_old} days old - consider refreshing",
                    "last_updated": latest_update.isoformat(),
                    "severity": "warning"
                })
            else:
                self.validation_results["passed"].append({
                    "check": "data_freshness",
                    "message": f"Data is fresh ({days_old} days old)",
                    "last_updated": latest_update.isoformat()
                })
                
        except Exception as e:
            self.validation_results["warnings"].append({
                "check": "data_freshness",
                "message": f"Could not check data freshness: {str(e)}",
                "severity": "warning"
            })


def validate_fund_data(db: Session) -> Dict[str, Any]:
    """Convenience function to run all validations"""
    validator = FundDataValidator(db)
    return validator.validate_all()


# Make sure to import or_ at the top
from sqlalchemy import or_
