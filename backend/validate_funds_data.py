#!/usr/bin/env python3
"""
Validate Fund Data
Comprehensive sanity checks for mutual fund master data

Usage:
    python validate_funds_data.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.utils.data_validator import validate_fund_data
from sqlalchemy import func
from app.models.models import FundMaster


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f" {text}")
    print(f"{'='*70}")


def main():
    """Main validation function"""
    print_header("MFHelper - Fund Data Validation")
    print("Checking mutual fund master data integrity...\n")
    
    db = SessionLocal()
    try:
        # Run validation
        print_header("Running Validation Checks")
        results = validate_fund_data(db)
        
        # Print results
        print(f"\nOverall Status: ", end="")
        if results['status'] == 'pass':
            print("✓ PASS")
        else:
            print("✗ FAIL")
        
        print(f"\nSummary:")
        print(f"  Total Checks: {results['total_checks']}")
        print(f"  Passed: {results['passed']} ✓")
        print(f"  Failed: {results['failed']} ✗")
        print(f"  Warnings: {results['warnings']} ⚠")
        
        # Show failed checks
        if results['details']['failed']:
            print_header("Failed Checks")
            for failure in results['details']['failed']:
                severity = failure.get('severity', 'error').upper()
                print(f"\n✗ [{severity}] {failure['check']}")
                print(f"  {failure['message']}")
                if 'data' in failure:
                    print(f"  Data: {failure['data']}")
        
        # Show warnings
        if results['details']['warnings']:
            print_header("Warnings")
            for warning in results['details']['warnings']:
                print(f"\n⚠  {warning['check']}")
                print(f"  {warning['message']}")
                if 'data' in warning:
                    print(f"  Data: {warning['data']}")
        
        # Show passed checks summary
        if results['details']['passed']:
            print_header("Passed Checks")
            print(f"✓ {len(results['details']['passed'])} checks passed successfully")
            for passed in results['details']['passed'][:5]:
                print(f"  - {passed['check']}: {passed['message']}")
            if len(results['details']['passed']) > 5:
                print(f"  ... and {len(results['details']['passed']) - 5} more")
        
        print("\n" + "="*70 + "\n")
        
        # Exit with appropriate code
        if results['status'] == 'fail':
            print("❌ Validation FAILED - please fix errors above")
            return 1
        elif results['warnings'] > 0:
            print("⚠️  Validation PASSED with warnings")
            return 0
        else:
            print("✅ All validation checks PASSED")
            return 0
        
    except Exception as e:
        print(f"\n❌ Error during validation: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
