"""Fix known data quality issues in fund_holdings.json"""
import json
from collections import Counter

with open("data/fund_holdings.json", "r", encoding="latin-1") as f:
    data = json.load(f)

funds = data["funds"]
removed_funds = []
fixed_funds = []

# ── 1. Remove corrupted PPFAS/Parag Parikh consolidated & liquid entries ──
# These have CAS statement metadata parsed as holdings
for bad_key in ["ppfas-consolidated", "parag-parikh-liquid-fund"]:
    if bad_key in funds:
        # Keep only holdings with valid weight (0-100) and non-numeric sector
        original = funds[bad_key]["holdings"]
        cleaned = []
        for h in original:
            w = h.get("weight", 0)
            s = h.get("sector", "")
            stock = h.get("stock", "")
            # Skip if: weight > 100, sector is numeric, stock is a date/returns label, or stock is "GRAND TOTAL"
            if w > 100:
                continue
            if s and s.replace(".", "").replace("-", "").isdigit():
                continue
            if "annualised" in stock.lower() or "market value" in stock.lower():
                continue
            if "since inception" in stock.lower() or "last" in stock.lower() and "year" in stock.lower():
                continue
            if stock.upper() == "GRAND TOTAL":
                continue
            if not s:
                continue
            cleaned.append(h)
        
        if len(cleaned) < len(original):
            diff = len(original) - len(cleaned)
            funds[bad_key]["holdings"] = cleaned
            funds[bad_key]["holdings_count"] = len(cleaned)
            fixed_funds.append(f"{bad_key}: removed {diff} corrupted entries, kept {len(cleaned)} valid holdings")

# ── 2. Find and flag duplicate fund clusters (don't remove, just report) ──
stock_sets = {}
for key, fund in funds.items():
    stocks = frozenset(h["stock"].strip().lower() for h in fund.get("holdings", []) if h.get("stock"))
    stock_sets[key] = stocks

dupe_groups = {}
for key, stocks in stock_sets.items():
    if len(stocks) == 0:
        continue
    found = False
    for gid, (gstocks, gkeys) in dupe_groups.items():
        if stocks == gstocks:
            gkeys.append(key)
            found = True
            break
    if not found:
        dupe_groups[len(dupe_groups)] = (stocks, [key])

print("\n=== Duplicate Fund Groups (identical holdings) ===")
for gid, (gstocks, gkeys) in dupe_groups.items():
    if len(gkeys) > 1:
        print(f"  Group ({len(gkeys)} funds, {len(gstocks)} stocks):")
        for k in gkeys:
            f = funds[k]
            print(f"    - {k}: {f.get('name')} ({f.get('amc')}, {f.get('category')})")

# ── 3. Fix duplicate stocks within a fund ──
for key, fund in funds.items():
    holdings = fund.get("holdings", [])
    seen = {}
    deduped = []
    for h in holdings:
        stock_lower = h.get("stock", "").strip().lower()
        if stock_lower in seen:
            # Keep the one with higher weight
            existing_idx = seen[stock_lower]
            if h.get("weight", 0) > deduped[existing_idx].get("weight", 0):
                deduped[existing_idx] = h
            fixed_funds.append(f"{key}: merged duplicate stock '{h.get('stock')}'")
        else:
            seen[stock_lower] = len(deduped)
            deduped.append(h)
    
    if len(deduped) < len(holdings):
        fund["holdings"] = deduped
        fund["holdings_count"] = len(deduped)

# ── 4. Trim whitespace in stock names and sectors ──
for key, fund in funds.items():
    for h in fund.get("holdings", []):
        if h.get("stock") and h["stock"] != h["stock"].strip():
            h["stock"] = h["stock"].strip()
            fixed_funds.append(f"{key}: trimmed stock name")
        if h.get("sector") and h["sector"] != h["sector"].strip():
            h["sector"] = h["sector"].strip()
            fixed_funds.append(f"{key}: trimmed sector name")

# ── 5. Fix holdings_count mismatches ──
for key, fund in funds.items():
    actual = len(fund.get("holdings", []))
    if fund.get("holdings_count") != actual:
        fund["holdings_count"] = actual
        fixed_funds.append(f"{key}: fixed holdings_count to {actual}")

# ── 6. Save as proper UTF-8 ──
with open("data/fund_holdings.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n=== Fixes Applied: {len(fixed_funds)} ===")
for fix in fixed_funds:
    print(f"  ✔ {fix}")

print(f"\nSaved as UTF-8. Total funds: {len(funds)}")
