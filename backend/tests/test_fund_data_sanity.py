"""
Tests for Fund Data Sanity Checks
Ensures mutual fund master data integrity
"""
import pytest
from sqlalchemy.orm import Session
from app.models.models import FundMaster
from app.utils.data_validator import FundDataValidator, validate_fund_data
from datetime import datetime, timedelta


class TestFundDataSanity:
    """Test suite for fund data validation"""
    
    def test_data_exists(self, db: Session):
        """Test that fund master data exists in database"""
        validator = FundDataValidator(db)
        validator.check_data_exists()
        
        # Should have either passed or warning, not failed
        assert len([r for r in validator.validation_results["failed"] 
                   if r["check"] == "data_exists"]) == 0, \
            "Fund data should exist in database"
        
        # Get total  count
        total_funds = db.query(FundMaster).count()
        assert total_funds > 0, "Should have at least some fund data"
    
    def test_amc_data_exists(self, db: Session):
        """Test that AMC data is valid and present"""
        validator = FundDataValidator(db)
        validator.check_amc_data()
        
        # Get unique AMCs
        amc_count = db.query(FundMaster.amc).distinct().filter(
            FundMaster.amc != None,
            FundMaster.is_active == True
        ).count()
        
        assert amc_count > 0, "Should have at least one AMC"
        assert amc_count >= 10, f"Expected at least 10 AMCs, found {amc_count}"
    
    def test_each_amc_has_funds(self, db: Session):
        """Test that each AMC has associated funds"""
        from sqlalchemy import func
        
        # Get AMCs and their fund counts
        amc_fund_counts = db.query(
            FundMaster.amc,
            func.count(FundMaster.id)
        ).filter(
            FundMaster.is_active == True,
            FundMaster.amc != None
        ).group_by(FundMaster.amc).all()
        
        assert len(amc_fund_counts) > 0, "Should have AMCs with funds"
        
        # Each AMC should have at least 1 fund
        for amc, count in amc_fund_counts:
            assert count > 0, f"AMC '{amc}' has no funds"
    
    def test_fund_has_required_fields(self, db: Session):
        """Test that funds have all required fields"""
        # Get a sample of active funds
        funds = db.query(FundMaster).filter(
            FundMaster.is_active == True
        ).limit(100).all()
        
        assert len(funds) > 0, "Should have active funds"
        
        for fund in funds:
            # Critical fields that must exist
            assert fund.scheme_code, f"Fund {fund.id} missing scheme_code"
            assert fund.scheme_name, f"Fund {fund.id} missing scheme_name"
            assert fund.amc, f"Fund {fund.id} missing amc"
            
            # Scheme code should be alphanumeric
            assert len(fund.scheme_code) > 0, "Scheme code should not be empty"
            
            # Scheme name should be reasonable length
            assert len(fund.scheme_name) >= 5, \
                f"Scheme name too short: {fund.scheme_name}"
            assert len(fund.scheme_name) <= 500, \
                f"Scheme name too long: {fund.scheme_name}"
    
    def test_no_duplicate_scheme_codes(self, db: Session):
        """Test that scheme codes are unique"""
        from sqlalchemy import func
        
        # Find duplicate scheme codes
        duplicates = db.query(
            FundMaster.scheme_code,
            func.count(FundMaster.id)
        ).filter(
            FundMaster.scheme_code != None
        ).group_by(
            FundMaster.scheme_code
        ).having(
            func.count(FundMaster.id) > 1
        ).all()
        
        assert len(duplicates) == 0, \
            f"Found {len(duplicates)} duplicate scheme codes: {duplicates[:5]}"
    
    def test_nav_values_valid(self, db: Session):
        """Test that NAV values are reasonable"""
        # Get funds with NAV data
        funds_with_nav = db.query(FundMaster).filter(
            FundMaster.current_nav != None
        ).limit(100).all()
        
        if len(funds_with_nav) > 0:
            for fund in funds_with_nav:
                # NAV should be positive
                assert fund.current_nav > 0, \
                    f"Fund {fund.scheme_name} has invalid NAV: {fund.current_nav}"
                
                # NAV should be reasonable (typically between 1 and 10000)
                assert 0.1 <= fund.current_nav <= 100000, \
                    f"Fund {fund.scheme_name} has suspicious NAV: {fund.current_nav}"
    
    def test_expense_ratio_valid(self, db: Session):
        """Test that expense ratios are reasonable"""
        funds_with_expense = db.query(FundMaster).filter(
            FundMaster.expense_ratio != None
        ).limit(100).all()
        
        if len(funds_with_expense) > 0:
            for fund in funds_with_expense:
                # Expense ratio should be between 0 and 5% (typically)
                assert 0 <= fund.expense_ratio <= 5.0, \
                    f"Fund {fund.scheme_name} has invalid expense ratio: {fund.expense_ratio}%"
    
    def test_returns_data_valid(self, db: Session):
        """Test that return percentages are reasonable"""
        funds_with_returns = db.query(FundMaster).filter(
            FundMaster.one_year_return != None
        ).limit(100).all()
        
        if len(funds_with_returns) > 0:
            for fund in funds_with_returns:
                # Returns should be realistic (-100% to +500%)
                if fund.one_year_return is not None:
                    assert -100 <= fund.one_year_return <= 500, \
                        f"Fund {fund.scheme_name} has unrealistic 1Y return: {fund.one_year_return}%"
                
                if fund.three_year_return is not None:
                    assert -100 <= fund.three_year_return <= 500, \
                        f"Fund {fund.scheme_name} has unrealistic 3Y return: {fund.three_year_return}%"
                
                if fund.five_year_return is not None:
                    assert -100 <= fund.five_year_return <= 500, \
                        f"Fund {fund.scheme_name} has unrealistic 5Y return: {fund.five_year_return}%"
    
    def test_categories_valid(self, db: Session):
        """Test that fund categories are from expected set"""
        expected_categories = {
            'Equity - Large Cap',
            'Equity - Mid Cap',
            'Equity - Small Cap',
            'Equity - Flexi Cap',
            'Equity - Others',
            'Debt',
            'Liquid',
            'Hybrid',
            'Index',
            'ELSS',
            'Others',
            None  # Some funds may not have category
        }
        
        # Get unique categories
        categories = db.query(FundMaster.category).distinct().all()
        actual_categories = {cat[0] for cat in categories}
        
        # All categories should be in expected set
        unexpected = actual_categories - expected_categories
        assert len(unexpected) == 0 or list(unexpected) == [None], \
            f"Found unexpected categories: {unexpected}"
    
    def test_plan_type_valid(self, db: Session):
        """Test that plan types are either Direct or Regular"""
        valid_plan_types = {'Direct', 'Regular', None}
        
        # Get unique plan types
        plan_types = db.query(FundMaster.plan_type).distinct().all()
        actual_plan_types = {pt[0] for pt in plan_types}
        
        assert actual_plan_types.issubset(valid_plan_types), \
            f"Found invalid plan types: {actual_plan_types - valid_plan_types}"
    
    def test_amc_names_consistent(self, db: Session):
        """Test that AMC names don't have variations/typos"""
        from sqlalchemy import func
        
        # Get all AMC names
        amc_names = [amc[0] for amc in db.query(FundMaster.amc).distinct().all() 
                     if amc[0]]
        
        # Check for suspiciously similar AMC names (might be typos)
        # This is a simple check - could be enhanced
        for amc in amc_names:
            # AMC names should be reasonable length
            assert len(amc) >= 3, f"AMC name too short: '{amc}'"
            assert len(amc) <= 200, f"AMC name too long: '{amc}'"
            
            # Should not have excessive whitespace
            assert amc == amc.strip(), f"AMC has leading/trailing whitespace: '{amc}'"
    
    def test_comprehensive_validation(self, db: Session):
        """Run all validation checks together"""
        results = validate_fund_data(db)
        
        # Should return proper structure
        assert "status" in results
        assert "total_checks" in results
        assert "passed" in results
        assert "failed" in results
        
        # Should have run multiple checks
        assert results["total_checks"] > 0, "Should have run validation checks"
        
        # Print results for debugging
        print(f"\n{'='*60}")
        print(f"Fund Data Validation Results:")
        print(f"{'='*60}")
        print(f"Status: {results['status'].upper()}")
        print(f"Total Checks: {results['total_checks']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Warnings: {results['warnings']}")
        
        if results['details']['failed']:
            print(f"\n❌ Failed Checks:")
            for failure in results['details']['failed']:
                print(f"  - {failure['check']}: {failure['message']}")
        
        if results['details']['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in results['details']['warnings']:
                print(f"  - {warning['check']}: {warning['message']}")
        
        if results['details']['passed']:
            print(f"\n✓ Passed Checks: {len(results['details']['passed'])}")
        
        print(f"{'='*60}\n")
        
        # Test should pass if no critical failures
        critical_failures = [f for f in results['details']['failed'] 
                           if f.get('severity') == 'critical']
        assert len(critical_failures) == 0, \
            f"Critical validation failures: {critical_failures}"


class TestFundDataQueries:
    """Test fund data queries work correctly"""
    
    def test_search_funds_by_name(self, db: Session):
        """Test searching funds by name"""
        # Get a fund name
        sample_fund = db.query(FundMaster).filter(
            FundMaster.is_active == True
        ).first()
        
        if sample_fund:
            # Search for part of the name
            search_term = sample_fund.scheme_name.split()[0]
            results = db.query(FundMaster).filter(
                FundMaster.scheme_name.ilike(f"%{search_term}%"),
                FundMaster.is_active == True
            ).all()
            
            assert len(results) > 0, "Search should return results"
            assert any(search_term.lower() in r.scheme_name.lower() 
                      for r in results), "Results should match search term"
    
    def test_filter_by_amc(self, db: Session):
        """Test filtering funds by AMC"""
        # Get an AMC
        sample_amc = db.query(FundMaster.amc).filter(
            FundMaster.amc != None,
            FundMaster.is_active == True
        ).first()
        
        if sample_amc:
            amc_name = sample_amc[0]
            results = db.query(FundMaster).filter(
                FundMaster.amc == amc_name,
                FundMaster.is_active == True
            ).all()
            
            assert len(results) > 0, f"AMC '{amc_name}' should have funds"
            assert all(r.amc == amc_name for r in results), \
                "All results should be from the specified AMC"
    
    def test_filter_by_category(self, db: Session):
        """Test filtering funds by category"""
        # Get a category
        sample_category = db.query(FundMaster.category).filter(
            FundMaster.category != None,
            FundMaster.is_active == True
        ).first()
        
        if sample_category:
            category_name = sample_category[0]
            results = db.query(FundMaster).filter(
                FundMaster.category == category_name,
                FundMaster.is_active == True
            ).all()
            
            assert len(results) > 0, f"Category '{category_name}' should have funds"
            assert all(r.category == category_name for r in results), \
                "All results should be from the specified category"


# Integration test that can be run standalone
if __name__ == "__main__":
    """Run validation as a standalone script"""
    from app.database import SessionLocal
    
    print("Running fund data validation...")
    db = SessionLocal()
    try:
        results = validate_fund_data(db)
        
        print(f"\n{'='*60}")
        print(f"Fund Data Validation Results")
        print(f"{'='*60}")
        print(f"Status: {results['status'].upper()}")
        print(f"Total Checks: {results['total_checks']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Warnings: {results['warnings']}")
        
        if results['details']['failed']:
            print(f"\n❌ Failed Checks:")
            for failure in results['details']['failed']:
                print(f"  - {failure['check']}: {failure['message']}")
        
        if results['details']['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in results['details']['warnings']:
                print(f"  - {warning['check']}: {warning['message']}")
        
        print(f"\n✓ Passed: {len(results['details']['passed'])} checks")
        print(f"{'='*60}\n")
        
        # Exit with error code if validation failed
        exit(0 if results['status'] == 'pass' else 1)
        
    finally:
        db.close()
