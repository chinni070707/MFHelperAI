"""
Debug PPFAS Excel parsing
"""
import pandas as pd
from pathlib import Path

filepath = Path(__file__).parent.parent / 'data' / 'portfolio_downloads' / 'PPFCF_January_2026.xls'

print(f"\nDebugging: {filepath}")
print("="*80)

# Read raw
df = pd.read_excel(filepath, sheet_name=0)

print(f"\nShape: {df.shape}")
print("\nFirst 15 rows (all columns):")

for idx in range(min(15, len(df))):
    row = df.iloc[idx]
    print(f"\nRow {idx}:")
    for col_idx, value in enumerate(row):
        if pd.notna(value):
            value_str = str(value)[:60]
            print(f"  Col {col_idx}: {value_str}")

# Find header
print("\n" + "="*80)
print("FINDING HEADER ROW")
print("="*80)

for idx in range(min(20, len(df))):
    row = df.iloc[idx]
    row_str = ' '. join(str(x) for x in row if pd.notna(x))
    
    if 'Instrument' in row_str or 'Industry' in row_str:
        print(f"\n[FOUND] Header at row {idx}:")
        print(f"   {row_str[:150]}")
        
        # Try parsing from this row
        df_parsed = pd.read_excel(filepath, sheet_name=0, header=idx)
        print(f"\nColumns after setting header={idx}:")
        for col in df_parsed.columns:
            print(f"   - {col}")
        
        print(f"\nFirst 5 data rows:")
        print(df_parsed.head().to_string())
        
        break
