"""
Fund Holdings Data Sanity Checker
=================================
Validates fund_holdings.json for data quality issues.

Checks:
  1. File-level: valid JSON, required top-level keys, version/date format
  2. Fund-level: required fields, valid fund key format, name/amc not empty
  3. Holding-level:
     - Stock name is text (not numeric, not empty, not too short)
     - Weight is a number in [0, 100]
     - Sector is non-empty text
     - No duplicate stocks within a fund
  4. Aggregate:
     - Sum of weights per fund should be ~100% (warn if <50% or >110%)
     - holdings_count matches actual holdings length
     - At least 5 holdings per fund (warn if fewer)
     - Sector names should be consistent (detect near-duplicates)
  5. Cross-fund:
     - Same stock should have consistent sector across funds
     - Detect suspiciously identical funds (>95% same holdings)

Usage:
    python scripts/validate_holdings.py [--fix] [--json]

    --fix   Auto-fix minor issues (trailing spaces, casing) and save
    --json  Output results as JSON instead of terminal report
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter
from difflib import SequenceMatcher

# ─── Path Setup ───
HOLDINGS_FILE = Path(__file__).parent.parent / "data" / "fund_holdings.json"


class HoldingsValidator:
    def __init__(self, filepath: Path = HOLDINGS_FILE):
        self.filepath = filepath
        self.data = None
        self.errors = []    # Must fix — data is wrong
        self.warnings = []  # Should review — suspicious
        self.info = []      # FYI — minor notes
        self.fixes_applied = []

    # ─── Load ───
    def load(self) -> bool:
        if not self.filepath.exists():
            self.errors.append(("FILE", "File not found", str(self.filepath)))
            return False
        try:
            # Try utf-8 first, fallback to utf-8-sig then latin-1
            for encoding in ["utf-8", "utf-8-sig", "latin-1"]:
                try:
                    with open(self.filepath, "r", encoding=encoding) as f:
                        self.data = json.load(f)
                    if encoding != "utf-8":
                        self.warnings.append(("FILE", f"File uses {encoding} encoding (should be utf-8)", ""))
                    return True
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
            self.errors.append(("FILE", "Cannot decode file with any encoding", ""))
            return False
        except json.JSONDecodeError as e:
            self.errors.append(("FILE", "Invalid JSON", str(e)))
            return False

    # ─── Top-Level Checks ───
    def check_top_level(self):
        required = ["funds"]
        for key in required:
            if key not in self.data:
                self.errors.append(("FILE", f"Missing required key: '{key}'", ""))
                return

        recommended = ["version", "last_updated", "source"]
        for key in recommended:
            if key not in self.data:
                self.warnings.append(("FILE", f"Missing recommended key: '{key}'", ""))

        funds = self.data.get("funds", {})
        if not isinstance(funds, dict):
            self.errors.append(("FILE", "'funds' should be a dict", type(funds).__name__))
            return

        if len(funds) == 0:
            self.errors.append(("FILE", "No funds found", ""))

        self.info.append(("FILE", f"Total funds: {len(funds)}", ""))

    # ─── Fund-Level Checks ───
    def check_fund(self, fund_key: str, fund: dict):
        prefix = f"Fund[{fund_key}]"

        # Key format
        if not re.match(r'^[a-z0-9\-]+$', fund_key):
            self.warnings.append((prefix, "Fund key has unusual characters", fund_key))

        # Required fields
        for field in ["name", "amc", "category", "holdings"]:
            if field not in fund:
                self.errors.append((prefix, f"Missing field: '{field}'", ""))

        name = fund.get("name", "")
        amc = fund.get("amc", "")
        category = fund.get("category", "")

        if not name or not isinstance(name, str):
            self.errors.append((prefix, "Empty or non-string fund name", repr(name)))
        elif name.strip() != name:
            self.warnings.append((prefix, "Fund name has leading/trailing spaces", repr(name)))

        if not amc or not isinstance(amc, str):
            self.errors.append((prefix, "Empty or non-string AMC", repr(amc)))

        if not category or not isinstance(category, str):
            self.warnings.append((prefix, "Empty or non-string category", repr(category)))

        holdings = fund.get("holdings", [])
        if not isinstance(holdings, list):
            self.errors.append((prefix, "Holdings is not a list", type(holdings).__name__))
            return

        declared_count = fund.get("holdings_count")
        actual_count = len(holdings)
        if declared_count is not None and declared_count != actual_count:
            self.warnings.append((prefix, f"holdings_count mismatch: declared={declared_count}, actual={actual_count}", ""))

        if actual_count == 0:
            self.errors.append((prefix, "Fund has 0 holdings", ""))
        elif actual_count < 5:
            self.warnings.append((prefix, f"Only {actual_count} holdings (suspiciously few)", ""))

        # Check as_of_date format if present
        as_of = fund.get("as_of_date", "")
        if as_of and not re.match(r'^\d{4}-\d{2}-\d{2}', str(as_of)):
            self.warnings.append((prefix, f"Unusual as_of_date format", repr(as_of)))

    # ─── Holding-Level Checks ───
    def check_holding(self, fund_key: str, idx: int, holding: dict):
        prefix = f"Fund[{fund_key}] Holding[{idx}]"

        if not isinstance(holding, dict):
            self.errors.append((prefix, "Holding is not a dict", type(holding).__name__))
            return None

        stock = holding.get("stock", "")
        weight = holding.get("weight")
        sector = holding.get("sector", "")

        # ── Stock name checks ──
        if not stock or not isinstance(stock, str):
            self.errors.append((prefix, "Empty or non-string stock name", repr(stock)))
        else:
            stripped = stock.strip()
            # Numeric stock name
            if stripped.replace(".", "").replace("-", "").replace(",", "").isdigit():
                self.errors.append((prefix, "Stock name is numeric (should be text)", repr(stock)))
            # Too short
            elif len(stripped) < 2:
                self.errors.append((prefix, "Stock name too short (<2 chars)", repr(stock)))
            # Contains only special chars
            elif re.match(r'^[\W\d_]+$', stripped):
                self.errors.append((prefix, "Stock name has no alphabetic chars", repr(stock)))
            # Leading/trailing whitespace
            elif stock != stripped:
                self.warnings.append((prefix, "Stock name has extra whitespace", repr(stock)))
            # Suspiciously long
            elif len(stripped) > 100:
                self.warnings.append((prefix, "Stock name suspiciously long (>100 chars)", f"{stripped[:50]}..."))

        # ── Weight checks ──
        if weight is None:
            self.errors.append((prefix, "Missing weight", f"stock={stock}"))
        elif not isinstance(weight, (int, float)):
            self.errors.append((prefix, "Weight is not a number", f"{repr(weight)} for {stock}"))
        else:
            if weight < 0:
                self.errors.append((prefix, "Negative weight", f"{weight}% for {stock}"))
            elif weight > 100:
                self.errors.append((prefix, "Weight > 100%", f"{weight}% for {stock}"))
            elif weight == 0:
                self.warnings.append((prefix, "Weight is exactly 0", f"for {stock}"))
            elif weight > 25:
                self.warnings.append((prefix, "Very high weight (>25%)", f"{weight}% for {stock}"))

        # ── Sector checks ──
        if not sector or not isinstance(sector, str):
            self.errors.append((prefix, "Empty or non-string sector", f"for stock={stock}"))
        elif sector.strip() != sector:
            self.warnings.append((prefix, "Sector has extra whitespace", repr(sector)))
        elif sector.strip().replace(".", "").replace("-", "").isdigit():
            self.errors.append((prefix, "Sector is numeric (should be text)", repr(sector)))

        return {"stock": stock.strip() if stock else "", "weight": weight or 0, "sector": sector.strip() if sector else ""}

    # ─── Aggregate Checks ───
    def check_fund_aggregates(self, fund_key: str, holdings_data: list):
        prefix = f"Fund[{fund_key}]"

        # Weight sum
        weights = [h["weight"] for h in holdings_data if h]
        total = sum(weights)
        if total < 50:
            self.warnings.append((prefix, f"Total weight only {total:.1f}% (expected ~100%)", "Data may be incomplete"))
        elif total > 110:
            self.errors.append((prefix, f"Total weight {total:.1f}% exceeds 110%", "Weights may be double-counted"))
        elif total > 100.5:
            self.warnings.append((prefix, f"Total weight {total:.1f}% slightly above 100%", "Minor rounding"))

        # Duplicate stocks
        stock_names = [h["stock"].lower() for h in holdings_data if h and h["stock"]]
        dupes = [name for name, count in Counter(stock_names).items() if count > 1]
        for dupe in dupes:
            self.errors.append((prefix, f"Duplicate stock: '{dupe}'", f"Appears {Counter(stock_names)[dupe]} times"))

    # ─── Cross-Fund Checks ───
    def check_cross_fund(self):
        # Build stock → sector mapping
        stock_sectors = defaultdict(set)
        fund_stock_sets = {}

        for fund_key, fund in self.data["funds"].items():
            stocks = set()
            for h in fund.get("holdings", []):
                stock = h.get("stock", "").strip()
                sector = h.get("sector", "").strip()
                if stock and sector:
                    stock_sectors[stock.lower()].add(sector)
                    stocks.add(stock.lower())
            fund_stock_sets[fund_key] = stocks

        # Inconsistent sector for same stock
        inconsistent = 0
        for stock, sectors in stock_sectors.items():
            if len(sectors) > 1:
                inconsistent += 1
                if inconsistent <= 10:  # Show first 10
                    self.warnings.append(("CROSS-FUND", f"Stock '{stock}' has inconsistent sectors", f"{sectors}"))
        if inconsistent > 10:
            self.warnings.append(("CROSS-FUND", f"... and {inconsistent - 10} more inconsistent sectors", ""))

        # Detect near-duplicate funds (>95% overlap)
        fund_keys = list(fund_stock_sets.keys())
        for i in range(len(fund_keys)):
            for j in range(i + 1, len(fund_keys)):
                k1, k2 = fund_keys[i], fund_keys[j]
                s1, s2 = fund_stock_sets[k1], fund_stock_sets[k2]
                if len(s1) == 0 or len(s2) == 0:
                    continue
                overlap = len(s1 & s2) / min(len(s1), len(s2))
                if overlap > 0.95:
                    self.warnings.append(("CROSS-FUND", f"Near-duplicate funds ({overlap*100:.0f}% overlap)", f"{k1} <-> {k2}"))

        # Detect near-duplicate sector names (typos)
        all_sectors = set()
        for fund in self.data["funds"].values():
            for h in fund.get("holdings", []):
                s = h.get("sector", "").strip()
                if s:
                    all_sectors.add(s)

        sector_list = sorted(all_sectors)
        for i in range(len(sector_list)):
            for j in range(i + 1, len(sector_list)):
                ratio = SequenceMatcher(None, sector_list[i].lower(), sector_list[j].lower()).ratio()
                if ratio > 0.85 and sector_list[i].lower() != sector_list[j].lower():
                    self.warnings.append(("SECTORS", f"Similar sector names (possible typo/inconsistency)", f"'{sector_list[i]}' vs '{sector_list[j]}'"))

        self.info.append(("CROSS-FUND", f"Unique sectors across all funds: {len(all_sectors)}", ""))
        self.info.append(("CROSS-FUND", f"Unique stocks across all funds: {len(stock_sectors)}", ""))

    # ─── Auto-Fix ───
    def apply_fixes(self):
        """Fix minor issues: trim whitespace, fix holdings_count"""
        for fund_key, fund in self.data["funds"].items():
            # Trim fund name
            if fund.get("name") and fund["name"] != fund["name"].strip():
                fund["name"] = fund["name"].strip()
                self.fixes_applied.append(f"{fund_key}: trimmed fund name")

            holdings = fund.get("holdings", [])
            for h in holdings:
                # Trim stock name
                if h.get("stock") and h["stock"] != h["stock"].strip():
                    h["stock"] = h["stock"].strip()
                    self.fixes_applied.append(f"{fund_key}: trimmed stock '{h['stock']}'")
                # Trim sector
                if h.get("sector") and h["sector"] != h["sector"].strip():
                    h["sector"] = h["sector"].strip()
                    self.fixes_applied.append(f"{fund_key}: trimmed sector '{h['sector']}'")

            # Fix holdings_count
            if fund.get("holdings_count") != len(holdings):
                fund["holdings_count"] = len(holdings)
                self.fixes_applied.append(f"{fund_key}: fixed holdings_count to {len(holdings)}")

        if self.fixes_applied:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)

    # ─── Run All ───
    def validate(self, auto_fix=False):
        if not self.load():
            return

        self.check_top_level()
        if not self.data.get("funds"):
            return

        for fund_key, fund in self.data["funds"].items():
            self.check_fund(fund_key, fund)
            holdings_data = []
            for idx, h in enumerate(fund.get("holdings", [])):
                result = self.check_holding(fund_key, idx, h)
                holdings_data.append(result)
            self.check_fund_aggregates(fund_key, [h for h in holdings_data if h])

        self.check_cross_fund()

        if auto_fix:
            self.apply_fixes()

    # ─── Report ───
    def print_report(self):
        total = len(self.errors) + len(self.warnings)

        print("=" * 70)
        print("  FUND HOLDINGS DATA VALIDATION REPORT")
        print("=" * 70)
        print(f"  File: {self.filepath.name}")
        print(f"  Funds: {len(self.data.get('funds', {})) if self.data else 0}")
        print()

        if self.errors:
            print(f"  ❌ ERRORS: {len(self.errors)}  (must fix)")
            print("-" * 70)
            for loc, msg, detail in self.errors:
                d = f" — {detail}" if detail else ""
                print(f"  ❌ [{loc}] {msg}{d}")
            print()

        if self.warnings:
            print(f"  ⚠️  WARNINGS: {len(self.warnings)}  (should review)")
            print("-" * 70)
            for loc, msg, detail in self.warnings:
                d = f" — {detail}" if detail else ""
                print(f"  ⚠️  [{loc}] {msg}{d}")
            print()

        if self.info:
            print(f"  ℹ️  INFO: {len(self.info)}")
            print("-" * 70)
            for loc, msg, detail in self.info:
                d = f" — {detail}" if detail else ""
                print(f"  ℹ️  [{loc}] {msg}{d}")
            print()

        if self.fixes_applied:
            print(f"  🔧 AUTO-FIXES APPLIED: {len(self.fixes_applied)}")
            print("-" * 70)
            for fix in self.fixes_applied:
                print(f"  🔧 {fix}")
            print()

        print("=" * 70)
        if self.errors:
            print(f"  RESULT: ❌ FAILED — {len(self.errors)} errors, {len(self.warnings)} warnings")
        elif self.warnings:
            print(f"  RESULT: ⚠️  PASSED WITH WARNINGS — {len(self.warnings)} warnings")
        else:
            print(f"  RESULT: ✅ ALL CHECKS PASSED")
        print("=" * 70)

    def to_json(self):
        return {
            "file": str(self.filepath),
            "errors": [{"location": l, "message": m, "detail": d} for l, m, d in self.errors],
            "warnings": [{"location": l, "message": m, "detail": d} for l, m, d in self.warnings],
            "info": [{"location": l, "message": m, "detail": d} for l, m, d in self.info],
            "fixes": self.fixes_applied,
            "passed": len(self.errors) == 0,
        }


if __name__ == "__main__":
    auto_fix = "--fix" in sys.argv
    as_json = "--json" in sys.argv

    validator = HoldingsValidator()
    validator.validate(auto_fix=auto_fix)

    if as_json:
        print(json.dumps(validator.to_json(), indent=2))
    else:
        validator.print_report()

    sys.exit(1 if validator.errors else 0)
