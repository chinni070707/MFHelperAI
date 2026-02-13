"""
Parse Axis Mutual Fund monthly portfolio XLS files → fund_holdings.json

Axis .xls format (xlrd):
  Row 0: Fund code + fund name
  Row 3: Headers
  Row 6+: Holdings — col1=Name, col2=ISIN, col3=Sector, col6=% to Net Assets (decimal)

Target funds (January 2026):
  axis-bluechip-fund       → Axis Large Cap Fund (renamed from Bluechip)
  axis-midcap-fund         → Axis Midcap Fund
  axis-small-cap-fund      → Axis Small Cap Fund
  axis-focused-25-fund     → Axis Focused Fund (renamed from Focused 25)
  axis-long-term-equity-fund → Axis ELSS Tax Saver Fund (renamed from Long Term Equity)
"""

import json
import xlrd
from pathlib import Path
from datetime import datetime

DOWNLOAD_DIR = Path(__file__).parent.parent / "data" / "downloads"
HOLDINGS_FILE = Path(__file__).parent.parent / "data" / "fund_holdings.json"
AS_OF_DATE = "2026-01-31"

SKIP_KEYWORDS = {
    "total", "equity", "listed", "awaiting", "net assets",
    "sub total", "futures", "options", "debt", "money market",
    "commercial paper", "certificate", "treasury", "repo",
    "treps", "unlisted", "privately", "(a)", "(b)", "(c)", "(d)",
    "mutual fund", "fund of fund",
}


def parse_axis_xls(filepath):
    """Parse an Axis monthly portfolio XLS file. Returns list of {stock, weight, sector}."""
    wb = xlrd.open_workbook(str(filepath))
    ws = wb.sheet_by_index(0)
    holdings = []

    for i in range(6, ws.nrows):
        name_raw = ws.cell_value(i, 1)
        isin_raw = ws.cell_value(i, 2)
        sector_raw = ws.cell_value(i, 3)
        weight_raw = ws.cell_value(i, 6)

        if not name_raw:
            continue
        name_str = str(name_raw).strip()
        if not name_str or len(name_str) < 3:
            continue
        name_lower = name_str.lower()
        if any(kw in name_lower for kw in SKIP_KEYWORDS):
            continue

        # Must have valid ISIN
        isin_str = str(isin_raw).strip() if isin_raw else ""
        if not (isin_str.startswith("IN") and len(isin_str) == 12):
            continue

        try:
            w = float(weight_raw) * 100  # decimal → percentage
        except (TypeError, ValueError):
            continue
        if w < 0.05:
            continue

        sector_str = str(sector_raw).strip() if sector_raw else "Unknown"
        holdings.append({
            "stock": name_str,
            "weight": round(w, 2),
            "sector": sector_str,
        })

    return sorted(holdings, key=lambda x: -x["weight"])


def main():
    # Load existing fund_holdings.json
    with open(HOLDINGS_FILE) as f:
        data = json.load(f)
    funds = data.setdefault("funds", {})

    axis_targets = [
        ("axis-bluechip-fund",
         "Axis Large Cap Fund (formerly Bluechip)", "Large Cap",
         "Monthly Portfolio - Axis Large Cap Fund - 31 January  2026"),
        ("axis-midcap-fund",
         "Axis Midcap Fund", "Mid Cap",
         "Monthly Portfolio - Axis Midcap Fund - 31 January  2026"),
        ("axis-small-cap-fund",
         "Axis Small Cap Fund", "Small Cap",
         "Monthly Portfolio - Axis Small Cap Fund - 31 January 2026"),
        ("axis-focused-25-fund",
         "Axis Focused Fund (formerly Focused 25)", "Focused",
         "Monthly Portfolio - Axis Focused Fund - 31 January  2026"),
        ("axis-long-term-equity-fund",
         "Axis ELSS Tax Saver Fund", "ELSS",
         "Monthly Portfolio - Axis ELSS Tax Saver Fund - 31 January  2026"),
    ]

    updated = []
    print("=== AXIS FUNDS ===")
    for fund_id, display_name, category, file_prefix in axis_targets:
        # Glob for the file (handles URL-decoded filenames with trailing chars)
        matches = list(DOWNLOAD_DIR.glob(f"{file_prefix}*.xls*"))
        if not matches:
            print(f"  SKIP (not found): {file_prefix[:60]}")
            continue
        filepath = matches[0]
        holdings = parse_axis_xls(filepath)
        if holdings:
            funds[fund_id] = {
                "name": display_name,
                "amc": "Axis Mutual Fund",
                "category": category,
                "holdings": holdings,
                "holdings_count": len(holdings),
                "as_of_date": AS_OF_DATE,
                "source": "Axis Mutual Fund Official Monthly Portfolio Disclosure",
            }
            updated.append(fund_id)
            print(f"  OK {display_name}: {len(holdings)} holdings, top: {holdings[0]['stock']} {holdings[0]['weight']}%")
        else:
            print(f"  WARN: no equity holdings for {file_prefix[:50]}")

    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    data["source"] = "HDFC + PPFAS + Axis Official Monthly Portfolio Disclosures"

    with open(HOLDINGS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Updated fund_holdings.json — {len(updated)} Axis funds added")
    for fid in updated:
        print(f"  {fid}: {funds[fid]['holdings_count']} holdings")
    print(f"Total funds in file: {len(funds)}")


if __name__ == "__main__":
    main()
