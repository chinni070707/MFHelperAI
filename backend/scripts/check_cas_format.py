"""
Check the CAS header format to understand why casparser fails
"""
import fitz  # PyMuPDF

cas_file = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
password = "YOUR_CAS_PASSWORD"

# Open PDF
doc = fitz.open(cas_file)

# Decrypt if needed
if doc.is_encrypted:
    doc.authenticate(password)

# Get first 2 pages
print("=" * 80)
print("CAS HEADER - First 2000 characters")
print("=" * 80)

text = ""
for page_num in range(min(2, len(doc))):
    page = doc[page_num]
    text += page.get_text()

# Show first 2000 chars to understand the format
print(text[:2000])

print("\n" + "=" * 80)
print("Looking for date patterns...")
print("=" * 80)

import re

# Try to find statement period
patterns = [
    r"(\d{2}-[A-Za-z]{3}-\d{4})\s+to\s+(\d{2}-[A-Za-z]{3}-\d{4})",  # casparser format
    r"from\s+(\d{2}[/-]\d{2}[/-]\d{4})\s+to\s+(\d{2}[/-]\d{2}[/-]\d{4})",
    r"Period:\s*(\d{2}[/-]\d{2}[/-]\d{4})\s+to\s+(\d{2}[/-]\d{2}[/-]\d{4})",
    r"for\s+the\s+period\s+from\s+(\d{2}-[a-zA-Z]{2,3}-\d{4})\s+to\s+(\d{2}-[a-zA-Z]{2,3}-\d{4})",
]

for pattern in patterns:
    if match := re.search(pattern, text, re.I):
        print(f"✅ Found date pattern: {pattern}")
        print(f"   Matches: {match.groups()}")
        break
else:
    print("❌ No standard date pattern found")

# Check for CAS type
if re.search(r"consolidated\s+account\s+statement", text, re.I):
    print("✅ Found 'Consolidated Account Statement'")
elif re.search(r"demat\s+account", text, re.I):
    print("✅ Found 'Demat Account' (NSDL/CDSL)")
else:
    print("❓ CAS type unknown")

doc.close()
