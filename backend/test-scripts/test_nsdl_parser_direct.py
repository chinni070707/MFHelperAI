"""
Test calling the NSDL parser directly
"""
from casparser.parsers.mupdf import cas_pdf_to_text
from casparser.process.nsdl_statement import process_nsdl_text
from casparser.enums import FileType
import json

cas_file = r"C:\Users\mahchi01\Downloads\CAS_DEC2025_AA01244995_TXN.pdf"
password = "YOUR_CAS_PASSWORD"

print("=" * 80)
print("Testing NSDL/CDSL parser directly")
print("=" * 80)

try:
    # Step 1: Extract text with file type detection
    print("\n1. Extracting text from PDF...")
    partial_data = cas_pdf_to_text(cas_file, password)
    
    print(f"   File Type Detected: {partial_data.file_type}")
    print(f"   Investor: {partial_data.investor_info.name}")
    print(f"   Lines extracted: {len(partial_data.lines)}")
    
    # Step 2: Process as NSDL if detected as CDSL/NSDL
    if partial_data.file_type in (FileType.CDSL, FileType.NSDL):
        print(f"\n2. Processing as {partial_data.file_type.name} format...")
        
        text = "\u2029".join(partial_data.lines)
        processed_data = process_nsdl_text(text)
        
        print(f"   SUCCESS!")
        print(f"   Period: {processed_data.statement_period.from_} to {processed_data.statement_period.to}")
        print(f"   Accounts: {len(processed_data.accounts)}")
        
        # Show account details - let's see what attributes exist
        for i, account in enumerate(processed_data.accounts):
            print(f"\n   Account {i+1}:")
            print(f"   {account}")
            print(f"   Type: {type(account)}")
            print(f"   Fields: {account.model_fields.keys() if hasattr(account, 'model_fields') else dir(account)}")
        
        # Save to file
        output_file = "cas_parsed_nsdl.json"
        with open(output_file, 'w') as f:
            json.dump(processed_data.model_dump(), f, indent=2, default=str)
        print(f"\n   Saved detailed data to: {output_file}")
        
    else:
        print(f"\n   ERROR: File detected as {partial_data.file_type}, not CDSL/NSDL")
        print(f"   Cannot proceed with NSDL parser")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
