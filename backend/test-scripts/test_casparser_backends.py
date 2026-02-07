"""
Test casparser with specific parser backend
"""
import casparser
from casparser import read_cas_pdf

cas_file = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
password = "YOUR_CAS_PASSWORD"

print("=" * 80)
print("Testing casparser with different backends")
print("=" * 80)

# Try with PyMuPDF parser (faster, already installed)
print("\n[1] Trying with PyMuPDF backend...")
try:
    data = read_cas_pdf(cas_file, password, force_pdfminer=False)
    print(f"[SUCCESS] SUCCESS with PyMuPDF!")
    print(f"   File Type: {data.file_type}")
    print(f"   Period: {data.statement_period.from_} to {data.statement_period.to}")
    print(f"   Folios: {len(data.folios)}")
except Exception as e:
    print(f"[ERROR] Failed: {e}")

# Try with pdfminer backend
print("\n[2] Trying with pdfminer backend...")
try:
    data = read_cas_pdf(cas_file, password, force_pdfminer=True)
    print(f"[SUCCESS] SUCCESS with pdfminer!")
    print(f"   File Type: {data.file_type}")
    print(f"   Period: {data.statement_period.from_} to {data.statement_period.to}")
    print(f"   Folios: {len(data.folios)}")
except Exception as e:
    print(f"[ERROR] Failed: {e}")

print("\n" + "=" * 80)
print("Conclusion: This CAS format needs special handling for CDSL/Demat accounts")
print("=" * 80)
