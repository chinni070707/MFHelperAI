"""
Refetch Fund Holdings from MoneyControl
========================================
Fetches real portfolio holdings data from MoneyControl for all funds
that have dummy/placeholder data, or for any specific fund on demand.

Usage:
    python scripts/refetch_holdings.py                  # Refetch all dummy funds
    python scripts/refetch_holdings.py --all             # Refetch ALL funds  
    python scripts/refetch_holdings.py --fund hdfc-top-100-fund   # Refetch one fund
    python scripts/refetch_holdings.py --list-dummy      # Just list dummy funds
    python scripts/refetch_holdings.py --dry-run          # Show what would be fetched
    python scripts/refetch_holdings.py --add axis-bluechip-fund --url https://...  # Add new fund with MC URL
    python scripts/refetch_holdings.py --fund my-fund --url https://...             # Fetch using custom URL
"""
import sys
import io

# Fix Windows terminal encoding for Unicode
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

HOLDINGS_FILE = Path(__file__).parent.parent / "data" / "fund_holdings.json"

# ═══════════════════════════════════════════════════════════════════════
# MoneyControl URL mapping for all funds
# Format: fund-key -> MoneyControl portfolio URL
# ═══════════════════════════════════════════════════════════════════════
MONEYCONTROL_URLS = {
    # ── HDFC ──
    "hdfc-flexi-cap-fund":              "https://www.moneycontrol.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth/portfolio-holdings/MHD1144",
    "hdfc-small-cap-fund":              "https://www.moneycontrol.com/mutual-funds/hdfc-small-cap-fund-direct-plan-growth/portfolio-holdings/MHD254",
    "hdfc-large-cap-fund":              "https://www.moneycontrol.com/mutual-funds/hdfc-index-fund-nifty-50-plan-direct-plan/portfolio-holdings/MHD1151",
    "hdfc-mid-cap-fund":                "https://www.moneycontrol.com/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-plan-growth/portfolio-holdings/MHD003",
    "hdfc-mid-cap-opportunities-fund":  "https://www.moneycontrol.com/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-plan-growth/portfolio-holdings/MHD1163",
    "hdfc-top-100-fund":                "https://www.moneycontrol.com/mutual-funds/hdfc-top-100-fund-direct-plan-growth/portfolio-holdings/MHD068",
    "hdfc-balanced-advantage-fund":     "https://www.moneycontrol.com/mutual-funds/hdfc-balanced-advantage-fund-direct-plan-growth/portfolio-holdings/MHD1154",
    "hdfc-large-and-mid-cap-fund":      "https://www.moneycontrol.com/mutual-funds/hdfc-large-and-mid-cap-fund-direct-growth/portfolio-holdings/MHD1163",
    "hdfc-multicap-fund":               "https://www.moneycontrol.com/mutual-funds/hdfc-multi-cap-fund-direct-growth/portfolio-holdings/MHD4174",
    "hdfc-elss-tax-saver":              "https://www.moneycontrol.com/mutual-funds/hdfc-elss-tax-saver-direct-growth/portfolio-holdings/MHD1147",
    "hdfc-focused-fund":                "https://www.moneycontrol.com/mutual-funds/hdfc-focused-30-fund-direct-plan-growth/portfolio-holdings/MHD1145",
    "hdfc-value-fund":                  "https://www.moneycontrol.com/mutual-funds/hdfc-capital-builder-value-fund-direct-plan-growth/portfolio-holdings/MHD1146",

    # ── ICICI Prudential ──
    "icici-prudential-bluechip-fund":       "https://www.moneycontrol.com/mutual-funds/icici-prudential-bluechip-fund-direct-plan-growth/portfolio-holdings/MPI008",
    "icici-prudential-equity--debt-fund":   "https://www.moneycontrol.com/mutual-funds/icici-prudential-equity-debt-fund-direct-plan-growth/portfolio-holdings/MPI035",
    "icici-prudential-flexicap-fund":       "https://www.moneycontrol.com/mutual-funds/icici-prudential-flexicap-fund-direct-plan-growth/portfolio-holdings/MPI3416",
    "icici-prudential-midcap-fund":         "https://www.moneycontrol.com/mutual-funds/icici-prudential-midcap-fund-direct-plan-growth/portfolio-holdings/MPI604",
    "icici-prudential-smallcap-fund":       "https://www.moneycontrol.com/mutual-funds/icici-prudential-smallcap-fund-direct-plan-growth/portfolio-holdings/MPI3264",
    "icici-prudential-large-cap-fund":      "https://www.moneycontrol.com/mutual-funds/icici-prudential-large-cap-fund-direct-plan-growth/portfolio-holdings/MPI3418",
    "icici-prudential-large--mid-cap-fund": "https://www.moneycontrol.com/mutual-funds/icici-prudential-large-mid-cap-fund-direct-plan-growth/portfolio-holdings/MPI3406",
    "icici-prudential-multicap-fund":       "https://www.moneycontrol.com/mutual-funds/icici-prudential-multicap-fund-direct-plan-growth/portfolio-holdings/MPI3417",
    "icici-prudential-elss-tax-saver-fund": "https://www.moneycontrol.com/mutual-funds/icici-prudential-long-term-equity-fund-tax-saving-direct-plan-growth/portfolio-holdings/MPI036",
    "icici-prudential-focused-equity-fund": "https://www.moneycontrol.com/mutual-funds/icici-prudential-focused-equity-fund-direct-plan-growth/portfolio-holdings/MPI3257",
    "icici-prudential-value-fund":          "https://www.moneycontrol.com/mutual-funds/icici-prudential-value-discovery-fund-direct-plan-growth/portfolio-holdings/MPI038",

    # ── SBI ──
    "sbi-bluechip-fund":            "https://www.moneycontrol.com/mutual-funds/sbi-bluechip-fund-direct-growth/portfolio-holdings/MSB1069",
    "sbi-flexi-cap-fund":           "https://www.moneycontrol.com/mutual-funds/sbi-flexicap-fund-direct-growth/portfolio-holdings/MSB1083",
    "sbi-small-cap-fund":           "https://www.moneycontrol.com/mutual-funds/sbi-small-cap-fund-direct-growth/portfolio-holdings/MSB1077",
    "sbi-midcap-fund":              "https://www.moneycontrol.com/mutual-funds/sbi-magnum-midcap-fund-direct-growth/portfolio-holdings/MSB1076",
    "sbi-large-cap-fund":           "https://www.moneycontrol.com/mutual-funds/sbi-large-cap-fund-direct-growth/portfolio-holdings/MSB4477",
    "sbi-large--midcap-fund":       "https://www.moneycontrol.com/mutual-funds/sbi-large-midcap-fund-direct-growth/portfolio-holdings/MSB1075",
    "sbi-multicap-fund":            "https://www.moneycontrol.com/mutual-funds/sbi-multicap-fund-direct-growth/portfolio-holdings/MSB4478",
    "sbi-elss-tax-saver-fund":      "https://www.moneycontrol.com/mutual-funds/sbi-long-term-equity-fund-direct-growth/portfolio-holdings/MSB1081",
    "sbi-focused-fund":             "https://www.moneycontrol.com/mutual-funds/sbi-focused-equity-fund-direct-growth/portfolio-holdings/MSB1071",
    "sbi-contra-fund":              "https://www.moneycontrol.com/mutual-funds/sbi-contra-direct-fund-direct-growth/portfolio-holdings/MSB1068",

    # ── Axis ──
    "axis-bluechip-fund":           "https://www.moneycontrol.com/mutual-funds/axis-bluechip-fund-direct-growth/portfolio-holdings/MAX117",
    "axis-midcap-fund":             "https://www.moneycontrol.com/mutual-funds/axis-midcap-fund-direct-growth/portfolio-holdings/MAX129",
    "axis-small-cap-fund":          "https://www.moneycontrol.com/mutual-funds/axis-small-cap-fund-direct-growth/portfolio-holdings/MAX335",
    "axis-flexi-cap-fund":          "https://www.moneycontrol.com/mutual-funds/axis-flexi-cap-fund-direct-growth/portfolio-holdings/MAX4344",
    "axis-focused-fund":            "https://www.moneycontrol.com/mutual-funds/axis-focused-25-fund-direct-growth/portfolio-holdings/MAX118",
    "axis-elss-tax-saver-fund":     "https://www.moneycontrol.com/mutual-funds/axis-long-term-equity-fund-direct-growth/portfolio-holdings/MAX116",
    "axis-value-fund":              "https://www.moneycontrol.com/mutual-funds/axis-value-fund-direct-growth/portfolio-holdings/MAX4345",
    "axis-large-cap-fund":          "https://www.moneycontrol.com/mutual-funds/axis-growth-opportunities-fund-direct-growth/portfolio-holdings/MAX437",
    "axis-large--mid-cap-fund":     "https://www.moneycontrol.com/mutual-funds/axis-growth-opportunities-fund-direct-growth/portfolio-holdings/MAX437",
    "axis-multicap-fund":           "https://www.moneycontrol.com/mutual-funds/axis-multicap-fund-direct-growth/portfolio-holdings/MAX4346",

    # ── Kotak ──
    "kotak-equity-opportunities-fund":  "https://www.moneycontrol.com/mutual-funds/kotak-equity-opportunities-fund-direct-growth/portfolio-holdings/MKO033",
    "kotak-small-cap-fund":             "https://www.moneycontrol.com/mutual-funds/kotak-small-cap-fund-direct-growth/portfolio-holdings/MKO200",
    "kotak-flexi-cap-fund":             "https://www.moneycontrol.com/mutual-funds/kotak-flexicap-fund-direct-growth/portfolio-holdings/MKO4206",
    "kotak-midcap-fund":                "https://www.moneycontrol.com/mutual-funds/kotak-emerging-equity-fund-direct-growth/portfolio-holdings/MKO126",
    "kotak-large-cap-fund":             "https://www.moneycontrol.com/mutual-funds/kotak-bluechip-fund-direct-growth/portfolio-holdings/MKO039",
    "kotak-large-midcap-fund":          "https://www.moneycontrol.com/mutual-funds/kotak-equity-opportunities-fund-direct-growth/portfolio-holdings/MKO033",
    "kotak-multicap-fund":              "https://www.moneycontrol.com/mutual-funds/kotak-multicap-fund-direct-growth/portfolio-holdings/MKO4205",
    "kotak-elss-tax-saver-fund":        "https://www.moneycontrol.com/mutual-funds/kotak-tax-saver-fund-direct-growth/portfolio-holdings/MKO004",
    "kotak-contra-fund":                "https://www.moneycontrol.com/mutual-funds/kotak-india-eq-contra-fund-direct-growth/portfolio-holdings/MKO008",
    "kotak-focused-fund":               "https://www.moneycontrol.com/mutual-funds/kotak-focused-equity-fund-direct-growth/portfolio-holdings/MKO4208",
    "kotak-aggressive-hybrid-fund":     "https://www.moneycontrol.com/mutual-funds/kotak-equity-hybrid-fund-direct-growth/portfolio-holdings/MKO041",

    # ── Mirae Asset ──
    "mirae-asset-emerging-bluechip-fund":   "https://www.moneycontrol.com/mutual-funds/mirae-asset-emerging-bluechip-fund-direct-growth/portfolio-holdings/MMI001",
    "mirae-asset-large-cap-fund":           "https://www.moneycontrol.com/mutual-funds/mirae-asset-large-cap-fund-direct-growth/portfolio-holdings/MMI002",
    "mirae-asset-flexi-cap-fund":           "https://www.moneycontrol.com/mutual-funds/mirae-asset-flexi-cap-fund-direct-growth/portfolio-holdings/MMI4335",
    "mirae-asset-midcap-fund":              "https://www.moneycontrol.com/mutual-funds/mirae-asset-midcap-fund-direct-growth/portfolio-holdings/MMI016",
    "mirae-asset-small-cap-fund":           "https://www.moneycontrol.com/mutual-funds/mirae-asset-small-cap-fund-direct-growth/portfolio-holdings/MMI4332",
    "mirae-asset-aggressive-hybrid-fund":   "https://www.moneycontrol.com/mutual-funds/mirae-asset-hybrid-equity-fund-direct-growth/portfolio-holdings/MMI004",

    # ── Nippon India ──
    "nippon-india-small-cap-fund":      "https://www.moneycontrol.com/mutual-funds/nippon-india-small-cap-fund-direct-growth/portfolio-holdings/MRC262",
    "nippon-india-large-cap-fund":      "https://www.moneycontrol.com/mutual-funds/nippon-india-large-cap-fund-direct-growth/portfolio-holdings/MRC055",
    "nippon-india-flexi-cap-fund":      "https://www.moneycontrol.com/mutual-funds/nippon-india-flexi-cap-fund-direct-growth/portfolio-holdings/MRC4305",
    "nippon-india-elss-tax-saver-fund": "https://www.moneycontrol.com/mutual-funds/nippon-india-elss-tax-saver-fund-direct-growth/portfolio-holdings/MRC4308",

    # ── Parag Parikh ──
    "parag-parikh-flexi-cap-fund":      "https://www.moneycontrol.com/mutual-funds/parag-parikh-flexi-cap-fund-direct-growth/portfolio-holdings/MPP002",
    "parag-parikh-elss-tax-saver-fund": "https://www.moneycontrol.com/mutual-funds/parag-parikh-elss-tax-saver-fund-direct-growth/portfolio-holdings/MPP4359",

    # ── Quant ──
    "quant-small-cap-fund":     "https://www.moneycontrol.com/mutual-funds/quant-small-cap-fund-direct-plan-growth/portfolio-holdings/MES006",
    "quant-flexi-cap-fund":     "https://www.moneycontrol.com/mutual-funds/quant-active-fund-direct-plan-growth/portfolio-holdings/MES003",
    "quant-mid-cap-fund":       "https://www.moneycontrol.com/mutual-funds/quant-mid-cap-fund-direct-plan-growth/portfolio-holdings/MES055",
    "quant-elss-tax-saver-fund":"https://www.moneycontrol.com/mutual-funds/quant-elss-tax-saver-fund-direct-plan-growth/portfolio-holdings/MES005",

    # ── Quantum ──
    "quantum-elss-tax-saver-fund":  "https://www.moneycontrol.com/mutual-funds/quantum-elss-tax-saver-fund-direct-plan-growth/portfolio-holdings/MQM003",
    "quantum-value-fund":           "https://www.moneycontrol.com/mutual-funds/quantum-long-term-equity-value-fund-direct-growth/portfolio-holdings/MQM001",
    "quantum-small-cap-fund":       "https://www.moneycontrol.com/mutual-funds/quantum-small-cap-fund-direct-plan-growth/portfolio-holdings/MQM4380",

    # ── Motilal Oswal ──
    "motilal-oswal-midcap-fund":        "https://www.moneycontrol.com/mutual-funds/motilal-oswal-midcap-fund-direct-growth/portfolio-holdings/MMO4340",
    "motilal-oswal-flexi-cap-fund":     "https://www.moneycontrol.com/mutual-funds/motilal-oswal-flexi-cap-fund-direct-growth/portfolio-holdings/MMO006",
    "motilal-oswal-small-cap-fund":     "https://www.moneycontrol.com/mutual-funds/motilal-oswal-small-cap-fund-direct-growth/portfolio-holdings/MMO4339",
    "motilal-oswal-large-cap-fund":     "https://www.moneycontrol.com/mutual-funds/motilal-oswal-large-cap-fund-direct-growth/portfolio-holdings/MMO076",
    "motilal-oswal-elss-tax-saver-fund":"https://www.moneycontrol.com/mutual-funds/motilal-oswal-elss-tax-saver-fund-direct-growth/portfolio-holdings/MMO070",
    "motilal-oswal-focused-fund":       "https://www.moneycontrol.com/mutual-funds/motilal-oswal-focused-fund-direct-growth/portfolio-holdings/MMO007",
}


class MoneyControlFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.moneycontrol.com/",
        })

    def scrape_holdings(self, url: str, fund_name: str, max_retries: int = 3) -> list | None:
        """Scrape holdings from a MoneyControl portfolio page."""
        for attempt in range(max_retries):
            try:
                resp = self.session.get(url, timeout=30)
                if resp.status_code == 503:
                    wait = 8 * (attempt + 1)
                    if attempt < max_retries - 1:
                        print(f"  [WAIT] 503 -- retrying in {wait}s (attempt {attempt + 1})...", end="", flush=True)
                        time.sleep(wait)
                        continue
                    print(f"  [ERR] HTTP 503 after {max_retries} attempts")
                    return None
                if resp.status_code != 200:
                    print(f"  [ERR] HTTP {resp.status_code}")
                    return None
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                print(f"  [ERR] Error: {e}")
                return None

        try:

            soup = BeautifulSoup(resp.text, "html.parser")

            # Strategy 1: Find table with "Stock Invested in" header (equity funds)
            # Prefer the table with the MOST rows (complete holdings list)
            # Strategy 2: Find table with "Instrument" header (hybrid/debt funds)
            holdings_table = None
            table_type = None
            best_row_count = 0

            for table in soup.find_all("table"):
                header = table.find("tr")
                if not header:
                    continue
                headers = [th.get_text(strip=True) for th in header.find_all(["th", "td"])]
                header_str = " ".join(headers).lower()

                if "stock invested in" in header_str and "% of total holdings" in header_str:
                    row_count = len(table.find_all("tr"))
                    if row_count > best_row_count:
                        best_row_count = row_count
                        holdings_table = table
                        table_type = "equity"
                        # Detect column layout
                        if "sector total" in header_str or "m-cap" in header_str:
                            table_type = "equity_extended"  # Has extra columns

            if not holdings_table:
                # Fallback: try "Instrument" table for hybrid funds
                for table in soup.find_all("table"):
                    header = table.find("tr")
                    if not header:
                        continue
                    headers = [th.get_text(strip=True) for th in header.find_all(["th", "td"])]
                    if "Instrument" in headers and "Sector" in headers and "% of Total Holding" in headers:
                        holdings_table = table
                        table_type = "hybrid"
                        break

            if not holdings_table:
                print(f"  [ERR] No holdings table found")
                return None

            holdings = []
            for row in holdings_table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue

                if table_type == "equity":
                    # Cols: Stock Invested in | Sector | Value(Mn) | % of Total Holdings | ...
                    stock = cols[0].get_text(strip=True).replace("#", "").strip()
                    # Remove leading dash (MoneyControl uses - prefix for some stocks)
                    stock = stock.lstrip("-").strip()
                    sector = cols[1].get_text(strip=True) if len(cols) > 1 else "Unknown"
                    weight_text = cols[3].get_text(strip=True) if len(cols) > 3 else "0"
                elif table_type == "equity_extended":
                    # Extended: Stock Invested in | Sector | Sector Total | Value(Mn) | % of Total Holdings | ...
                    stock = cols[0].get_text(strip=True).replace("#", "").strip()
                    stock = stock.lstrip("-").strip()
                    sector = cols[1].get_text(strip=True) if len(cols) > 1 else "Unknown"
                    weight_text = cols[4].get_text(strip=True) if len(cols) > 4 else "0"
                else:
                    # Hybrid: Instrument | Type | Sector | Rating | ... | % of Total Holding
                    stock = cols[0].get_text(strip=True)
                    sector = cols[2].get_text(strip=True) if len(cols) > 2 else "Unknown"
                    weight_text = cols[6].get_text(strip=True) if len(cols) > 6 else "0"

                # Skip summary/non-stock rows
                skip_keywords = ["total", "equity", "debt", "cash", "net", "treps", "repo",
                                "grand", "no new", "no stocks", "bond -", "certificate"]
                if any(s in stock.lower() for s in skip_keywords):
                    continue
                if not stock or len(stock) < 3:
                    continue

                try:
                    weight = float(weight_text.replace("%", "").strip())
                except ValueError:
                    continue

                if weight >= 0.05:
                    holdings.append({"stock": stock, "weight": round(weight, 2), "sector": sector})

            return holdings if len(holdings) >= 3 else None

        except Exception as e:
            print(f"  [ERR] {e}")
            return None


def identify_dummy_funds(data: dict) -> list[str]:
    """Return fund keys that have duplicate/placeholder data."""
    stock_sigs = {}
    for key, fund in data["funds"].items():
        stocks = frozenset(h["stock"].strip().lower() for h in fund.get("holdings", []) if h.get("stock"))
        sig = hash(stocks)
        if sig not in stock_sigs:
            stock_sigs[sig] = []
        stock_sigs[sig].append(key)

    dummy = set()
    for sig, keys in stock_sigs.items():
        if len(keys) > 1:
            dummy.update(keys)
    return sorted(dummy)


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    fetch_all = "--all" in args
    list_only = "--list-dummy" in args
    specific_fund = None
    custom_url = None
    add_fund = None
    for i, a in enumerate(args):
        if a == "--fund" and i + 1 < len(args):
            specific_fund = args[i + 1]
        elif a == "--url" and i + 1 < len(args):
            custom_url = args[i + 1]
        elif a == "--add" and i + 1 < len(args):
            add_fund = args[i + 1]

    # Load current data
    with open(HOLDINGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # --add mode: add a new fund entry with a custom URL
    if add_fund and custom_url:
        print(f"\n  Adding new fund: {add_fund}")
        print(f"  URL: {custom_url}")
        fetcher = MoneyControlFetcher()
        holdings = fetcher.scrape_holdings(custom_url, add_fund)
        if holdings and len(holdings) >= 3:
            name = add_fund.replace('-', ' ').title()
            data["funds"][add_fund] = {
                "name": name,
                "amc": "",
                "category": "",
                "holdings": holdings,
                "holdings_count": len(holdings),
                "as_of_date": datetime.now().strftime("%Y-%m-%d"),
                "source": "MoneyControl Scraping",
            }
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            with open(HOLDINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  OK: {len(holdings)} holdings saved")
        else:
            print(f"  FAILED: no valid holdings found")
        return

    dummy_keys = identify_dummy_funds(data)

    if list_only:
        print(f"\n{'=' * 70}")
        print(f"  DUMMY FUNDS: {len(dummy_keys)}")
        print(f"{'=' * 70}")
        for k in dummy_keys:
            f = data["funds"][k]
            print(f"  X {k}: {f['name']} ({f.get('amc')}, {len(f.get('holdings', []))} holdings)")
        return

    # Determine which funds to fetch
    if specific_fund:
        to_fetch = [specific_fund]
    elif fetch_all:
        to_fetch = [k for k in data["funds"].keys() if k in MONEYCONTROL_URLS]
    else:
        to_fetch = [k for k in dummy_keys if k in MONEYCONTROL_URLS]
        # Also check if any fund key in the data isn't in our URL map
        unmapped_dummy = [k for k in dummy_keys if k not in MONEYCONTROL_URLS]
        if unmapped_dummy:
            print(f"\n  WARNING: {len(unmapped_dummy)} dummy funds have no MoneyControl URL:")
            for k in unmapped_dummy:
                print(f"    - {k}")

    if not to_fetch:
        print("\n  [OK] No funds need refetching!")
        return

    print(f"\n{'=' * 70}")
    print(f"  REFETCHING {len(to_fetch)} FUNDS FROM MONEYCONTROL")
    print(f"{'=' * 70}")

    if dry_run:
        for k in to_fetch:
            url = MONEYCONTROL_URLS.get(k, "NO URL")
            name = data["funds"].get(k, {}).get("name", k)
            print(f"  Would fetch: {name}")
            print(f"    URL: {url}")
        print(f"\n  (dry run — no changes made)")
        return

    fetcher = MoneyControlFetcher()
    success = 0
    failed = 0
    skipped = 0

    for key in to_fetch:
        url = custom_url if (specific_fund and custom_url) else MONEYCONTROL_URLS.get(key)
        if not url:
            print(f"\n  WARNING: {key}: no MoneyControl URL configured, skipping")
            print(f"    Use: python scripts/refetch_holdings.py --fund {key} --url <moneycontrol-url>")
            skipped += 1
            continue

        fund = data["funds"].get(key, {})
        name = fund.get("name", key)
        amc = fund.get("amc", "")
        category = fund.get("category", "")

        print(f"\n  Fetching: {name} ... ", end="", flush=True)

        holdings = fetcher.scrape_holdings(url, name)

        if holdings and len(holdings) >= 3:
            data["funds"][key] = {
                "name": name,
                "amc": amc,
                "category": category,
                "holdings": holdings,
                "holdings_count": len(holdings),
                "as_of_date": datetime.now().strftime("%Y-%m-%d"),
                "source": "MoneyControl Scraping",
            }
            print(f"OK: {len(holdings)} holdings")
            success += 1
        else:
            print(f"FAILED (got {len(holdings) if holdings else 0} holdings)")
            failed += 1

        time.sleep(5)  # Rate limit — MoneyControl throttles at faster rates

    # Save
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(HOLDINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"  RESULTS: {success} updated, {failed} failed, {skipped} skipped")
    print(f"{'=' * 70}")

    if success > 0:
        print(f"\n  Saved to {HOLDINGS_FILE}")
        print(f"  Run 'python scripts/validate_holdings.py' to verify data quality")


if __name__ == "__main__":
    main()
