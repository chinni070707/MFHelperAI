"""
Debug why casparser isn't detecting CDSL format properly
"""
import fitz
import re

cas_file = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
password = "AOLPC2904E"

doc = fitz.open(cas_file)
doc.authenticate(password)

# Get first page
page = doc[0]
text_page = page.get_textpage()
page_dict = text_page.extractDICT(sort=True)

print("=" * 80)
print("Checking for file type detection strings in first page")
print("=" * 80)

# Check all blocks for the detection strings
for i, block in enumerate(page_dict["blocks"]):
    block_str = str(block)
    
    if "Central Depository Services" in block_str:
        print(f"\nFOUND: 'Central Depository Services' in block {i}")
        print(f"   This should trigger CDSL detection")
    
    if "NSDL" in block_str:
        print(f"\nFOUND: 'NSDL' in block {i}")
    
    if "CAMSCASWS" in block_str:
        print(f"\nFOUND: 'CAMSCASWS' in block {i}")
    
    if "KFINCASWS" in block_str:
        print(f"\nFOUND: 'KFINCASWS' in block {i}")

print("\n" + "=" * 80)
print("Actual full text of first 3 blocks:")
print("=" * 80)
for i, block in enumerate(page_dict["blocks"][:3]):
    print(f"\nBlock {i}:")
    print(block)
    print("-" * 40)

doc.close()
