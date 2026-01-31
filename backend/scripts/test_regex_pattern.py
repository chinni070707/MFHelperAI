"""
Test if DEMAT_STATEMENT_PERIOD_RE regex matches our CAS
"""
import re
import fitz

cas_file = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
password = "YOUR_CAS_PASSWORD"

# Pattern from casparser
DEMAT_STATEMENT_PERIOD_RE = (
    r"for\s+the\s+period\s+from\s+(?P<from>\d{2}-[a-zA-Z0-9]{2,3}-\d{4})"
    r"\s+to\s+(?P<to>\d{2}-[a-zA-Z0-9]{2,3}-\d{4})"
)

# Open PDF and extract text
doc = fitz.open(cas_file)
doc.authenticate(password)

text = ""
for page_num in range(min(2, len(doc))):
    page = doc[page_num]
    text += page.get_text()

# Test the regex
print("=" * 80)
print("Testing DEMAT_STATEMENT_PERIOD_RE regex")
print("=" * 80)
print(f"\nPattern: {DEMAT_STATEMENT_PERIOD_RE}")

# Try to find it in the text
if match := re.search(DEMAT_STATEMENT_PERIOD_RE, text[:1000], re.I | re.MULTILINE):
    print(f"\nMATCH FOUND!")
    print(f"From: {match.group('from')}")
    print(f"To: {match.group('to')}")
else:
    print(f"\nNO MATCH FOUND in first 1000 chars")
    
    # Show what we're looking at
    print(f"\nSearching in text:")
    print("="*40)
    print(text[:1000])
    print("="*40)
    
    # Try to find any "period from" pattern
    if period_match := re.search(r"(period\s+from.{0,100})", text[:2000], re.I):
        print(f"\n\nFound text with 'period from':")
        print(period_match.group(0))
        
    # Try modified patterns
    alternative_patterns = [
        r"period\s+from\s+(\d{2}-\d{2}-\d{4})\s+to\s+(\d{2}-\d{2}-\d{4})",
        r"for\s+the\s+period\s+from\s+(\d{2}-[a-zA-Z]{3}-\d{4})\s+to\s+(\d{2}-[a-zA-Z]{3}-\d{4})",
        r"from\s+(\d{2}-\d{2}-\d{4})\s+to\s+(\d{2}-\d{2}-\d{4})",
    ]
    
    print(f"\n\nTrying alternative patterns:")
    for i, pattern in enumerate(alternative_patterns):
        if alt_match := re.search(pattern, text[:2000], re.I):
            print(f"Pattern {i+1} MATCHED: {alt_match.groups()}")

doc.close()
