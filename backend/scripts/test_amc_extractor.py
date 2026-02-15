"""
Quick test of AMC Extractor functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.amc_extractor import AmcExtractor

# Test cases
test_cases = [
    "Axis Long Term Equity Fund",
    "HDFC Tax Saver ELSS Direct Plan",
    "Parag Parikh Flexi Cap Fund",
    "Kotak Standard Multicap Fund",
    "SBI Focused Equity Fund",
    "Mirae Asset Large Cap Fund",
    "ICICI Prudential Banking & Financial Services Fund",
    "Quant Small Cap Fund",
    "Groww Nifty 50 Index Fund",
]

print("\n" + "="*70)
print("AMC EXTRACTOR TEST")
print("="*70 + "\n")

for fund_name in test_cases:
    amc = AmcExtractor.extract(fund_name)
    is_valid = "✅" if AmcExtractor.is_valid(amc) else "❌"
    print(f"{is_valid} {fund_name:50} → {amc}")

print("\n" + "="*70)
print(f"Total known AMCs: {len(AmcExtractor.get_all_known_amcs())}")
print("="*70 + "\n")

# Test invalid terms
print("\nTesting invalid AMC detection:")
invalid_test = ["Cap", "Tax", "ELSS", "Equity", "Midcap", "Value"]
for term in invalid_test:
    is_valid = AmcExtractor.is_valid(term)
    status = "❌ INVALID" if not is_valid else "✅ VALID"
    print(f"{status}: '{term}'")
