"""
Parse HDFC and PPFAS portfolio Excel files, update fund_holdings.json

HDFC format (openpyxl):
  Row 0: Fund name
  Row 1: Date string ("Portfolio as on 31-Jan-2026")
  Row 4: Headers
  Row 7+: Holdings — col1=ISIN, col3=Name, col4=Sector, col7=% to NAV

PPFAS Consolidated format (xlrd, .xls):
  Row 0: Fund name
  Row 3: Headers
  Row 6+: Holdings — col1=Name, col2=ISIN, col3=Sector, col6=% to Net Assets (decimal)
"""

import json
import xlrd
import openpyxl
from pathlib import Path
from datetime import datetime

DOWNLOAD_DIR = Path(__file__).parent.parent / "data" / "downloads"
HOLDINGS_FILE = Path(__file__).parent.parent / "data" / "fund_holdings.json"
AS_OF_DATE = "2026-01-31"


# ── HDFC parser ─────────────────────────────────────────────────────────────

def parse_hdfc_xlsx(filepath):
    """Parse an HDFC monthly portfolio Excel file (openpyxl format).

    Returns list of {stock, weight, sector} dicts.
    """
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    holdings = []
    skip_keywords = {
        "total", "equity", "listed", "awaiting", "net assets",
        "sub total", "futures", "options", "unlisted", "privately",
        "debt", "money market", "other", "repo", "(a)", "(b)", "(c)",
    }

    for row in ws.iter_rows(values_only=True):
        isin = row[1] if len(row) > 1 else None
        name = row[3] if len(row) > 3 else None
        sector = row[4] if len(row) > 4 else None
        weight = row[7] if len(row) > 7 else None

        if not isin or not name:
            continue

        isin_str = str(isin).strip()
        name_str = str(name).strip()
        # ISIN starts with country code (IN for India, US, etc.)
        if not (isin_str.startswith("IN") and len(isin_str) == 12):
            continue

        name_lower = name_str.lower()
        if any(kw in name_lower for kw in skip_keywords):
            continue

        try:
            w = float(weight)
        except (TypeError, ValueError):
            continue

        if w < 0.05:
            continue

        sector_str = str(sector).strip() if sector else "Unknown"
        # Clean up sector — sometimes it has extra spaces or special chars
        sector_str = sector_str.strip("£").strip()

        holdings.append({
            "stock": name_str.strip("£ "),
            "weight": round(w, 2),
            "sector": sector_str,
        })

    return sorted(holdings, key=lambda x: -x["weight"])


# ── PPFAS (xlrd) parser ──────────────────────────────────────────────────────

def parse_ppfas_sheet(ws):
    """Parse one sheet from PPFAS consolidated XLS.

    Row 3: headers; row 6+: data.
    col1=Name, col2=ISIN, col3=Sector, col6=% decimal
    Returns list of {stock, weight, sector}.
    """
    skip_keywords = {
        "total", "equity", "listed", "awaiting", "net assets",
        "sub total", "futures", "options", "debt", "money market",
        "commercial paper", "certificate", "treasury", "repo",
        "treps", "unlisted", "privately", "(a)", "(b)", "(c)", "(d)",
        "mutual fund", "fund of fund",
    }
    holdings = []

    for i in range(6, ws.nrows):
        name_raw = ws.cell_value(i, 1)
        isin_raw = ws.cell_value(i, 2)
        sector_raw = ws.cell_value(i, 3)
        weight_raw = ws.cell_value(i, 6)

        if not name_raw:
            continue

        name_str = str(name_raw).strip()
        name_lower = name_str.lower()
        if any(kw in name_lower for kw in skip_keywords) or len(name_str) < 3:
            continue

        # Validate ISIN
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


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Load existing fund_holdings.json
    if HOLDINGS_FILE.exists():
        with open(HOLDINGS_FILE) as f:
            data = json.load(f)
    else:
        data = {"version": "2026-02", "funds": {}}

    funds = data.setdefault("funds", {})
    updated = []

    # ── HDFC ────────────────────────────────────────────────────────────────
    hdfc_files = {
        "hdfc-flexi-cap-fund": (
            "Monthly HDFC Flexi Cap Fund - 31 January 2026.xlsx",
            "HDFC Flexi Cap Fund", "HDFC Mutual Fund", "Flexi Cap",
        ),
        "hdfc-top-100-fund": (
            "Monthly HDFC Large Cap Fund - 31 January 2026.xlsx",
            "HDFC Large Cap Fund (formerly Top 100)", "HDFC Mutual Fund", "Large Cap",
        ),
        "hdfc-mid-cap-opportunities-fund": (
            "Monthly HDFC Mid Cap Fund - 31 January 2026.xlsx",
            "HDFC Mid Cap Fund", "HDFC Mutual Fund", "Mid Cap",
        ),
        "hdfc-small-cap-fund": (
            "Monthly HDFC Small Cap Fund - 31 January 2026.xlsx",
            "HDFC Small Cap Fund", "HDFC Mutual Fund", "Small Cap",
        ),
        "hdfc-balanced-advantage-fund": (
            "Monthly HDFC Balanced Advantage Fund - 31 January 2026.xlsx",
            "HDFC Balanced Advantage Fund", "HDFC Mutual Fund", "Dynamic Asset Allocation",
        ),
    }

    print("=== HDFC FUNDS ===")
    for fund_id, (filename, display_name, amc, category) in hdfc_files.items():
        filepath = DOWNLOAD_DIR / filename
        if not filepath.exists():
            print(f"  SKIP (not found): {filename}")
            continue
        holdings = parse_hdfc_xlsx(filepath)
        if holdings:
            funds[fund_id] = {
                "name": display_name,
                "amc": amc,
                "category": category,
                "holdings": holdings,
                "holdings_count": len(holdings),
                "as_of_date": AS_OF_DATE,
                "source": "HDFC Official Monthly Portfolio Disclosure",
            }
            updated.append(fund_id)
            print(f"  OK {display_name}: {len(holdings)} holdings, top: {holdings[0]['stock']} {holdings[0]['weight']}%")
        else:
            print(f"  WARN no holdings parsed for {filename}")

    # ── PPFAS Consolidated ───────────────────────────────────────────────────
    ppfas_file = DOWNLOAD_DIR / "PPFAS_Monthly_Portfolio_Report_January_31_2026.xls"
    ppfas_sheet_map = {
        "PPFCF": ("parag-parikh-flexi-cap-fund", "Parag Parikh Flexi Cap Fund", "Flexi Cap"),
        "PPTSF": ("parag-parikh-tax-saver-fund", "Parag Parikh ELSS Tax Saver Fund", "ELSS"),
        "PPAF":  ("parag-parikh-arbitrage-fund", "Parag Parikh Arbitrage Fund", "Arbitrage"),
    }

    print("\n=== PPFAS FUNDS (from Consolidated) ===")
    if ppfas_file.exists():
        wb = xlrd.open_workbook(str(ppfas_file))
        for sheet_name, (fund_id, display_name, category) in ppfas_sheet_map.items():
            try:
                ws = wb.sheet_by_name(sheet_name)
                holdings = parse_ppfas_sheet(ws)
                if holdings:
                    funds[fund_id] = {
                        "name": display_name,
                        "amc": "Parag Parikh Mutual Fund",
                        "category": category,
                        "holdings": holdings,
                        "holdings_count": len(holdings),
                        "as_of_date": AS_OF_DATE,
                        "source": "PPFAS Official Monthly Portfolio Disclosure",
                    }
                    updated.append(fund_id)
                    print(f"  OK {display_name}: {len(holdings)} holdings, top: {holdings[0]['stock']} {holdings[0]['weight']}%")
                else:
                    print(f"  WARN no equity holdings for {sheet_name}")
            except Exception as e:
                print(f"  ERR {sheet_name}: {e}")
    else:
        print("  SKIP: PPFAS consolidated file not found")

    # ── PPFAS PPLF (Liquid Fund, old .xls) ──────────────────────────────────
    pplf_file = DOWNLOAD_DIR / "PPLF_PPFAS_Monthly_Portfolio_Report_January_31_2026.xls"
    print("\n=== PPFAS PPLF (Liquid Fund) ===")
    if pplf_file.exists():
        wb2 = xlrd.open_workbook(str(pplf_file))
        ws = wb2.sheet_by_index(0)
        # Liquid fund holds debt/MM instruments — parse with same col layout
        # col1=Name, col3=Rating, col4=Quantity, col5=Value, col6=% to Net Assets
        debt_holdings = []
        for i in range(6, ws.nrows):
            name_raw = ws.cell_value(i, 1)
            rating_raw = ws.cell_value(i, 3)
            weight_raw = ws.cell_value(i, 6)

            if not name_raw:
                continue
            name_str = str(name_raw).strip()
            if not name_str or len(name_str) < 5:
                continue
            skip_kw = {"sub total", "total", "(a)", "(b)", "nil", "debt", "money market",
                       "certificate of deposit", "commercial paper", "treasury"}
            if any(k in name_str.lower() for k in skip_kw):
                continue
            try:
                w = float(weight_raw) * 100
            except (TypeError, ValueError):
                continue
            if w < 0.01:
                continue
            debt_holdings.append({
                "stock": name_str,
                "weight": round(w, 2),
                "sector": str(rating_raw).strip() if rating_raw else "Debt",
            })

        if debt_holdings:
            fund_id = "parag-parikh-liquid-fund"
            funds[fund_id] = {
                "name": "Parag Parikh Liquid Fund",
                "amc": "Parag Parikh Mutual Fund",
                "category": "Liquid",
                "holdings": sorted(debt_holdings, key=lambda x: -x["weight"]),
                "holdings_count": len(debt_holdings),
                "as_of_date": AS_OF_DATE,
                "source": "PPFAS Official Monthly Portfolio Disclosure",
            }
            updated.append(fund_id)
            print(f"  OK Parag Parikh Liquid Fund: {len(debt_holdings)} debt instruments")
        else:
            print("  WARN: no instruments parsed for PPLF")
    else:
        print("  SKIP: PPLF file not found")

    # ── Save ─────────────────────────────────────────────────────────────────
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    data["source"] = "HDFC Official Monthly Portfolio Disclosure + PPFAS Official Monthly Portfolio Disclosure"

    with open(HOLDINGS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Updated fund_holdings.json — {len(updated)} funds refreshed:")
    for fid in updated:
        print(f"  {fid}: {funds[fid]['holdings_count']} holdings")
    print(f"Total funds in file: {len(funds)}")


if __name__ == "__main__":
    main()
