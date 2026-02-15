"""
Fund Metrics Scraper - Compute Risk Metrics from MFAPI NAV History

Fetches NAV history from MFAPI (api.mfapi.in) for all mutual funds and
computes comprehensive risk/return metrics:

  - Returns: 1M, 3M, 6M, 1Y, 3Y, 5Y (absolute + CAGR)
  - Risk: Standard Deviation, Max Drawdown
  - Risk-Adjusted: Sharpe Ratio, Sortino Ratio, Information Ratio
  - Market: Beta, Alpha, R-squared (vs Nifty 50 benchmark)
  - Fund Info: NAV, AUM, Category, Fund House

Data sources:
  - MFAPI (api.mfapi.in) - Free, open API for NAV history
  - AMFI (amfiindia.com) - Official NAV data with ISIN codes
  - Our moneycontrol_fund_codes.json - Fund list with categories

Output:
  - backend/data/fund_metrics.json  (comprehensive fund metrics)
  - Optionally loads into FundMaster database table

Usage:
  python backend/scripts/scrape_fund_metrics.py                    # All funds
  python backend/scripts/scrape_fund_metrics.py --limit 10         # First 10
  python backend/scripts/scrape_fund_metrics.py --fund-code MHD1161  # Single fund
  python backend/scripts/scrape_fund_metrics.py --force             # Rescrape all
"""
import requests
import json
import math
import statistics
import time
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory for database imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RISK_FREE_RATE = 6.5       # India 10Y govt bond yield (~6.5% as of 2026)
TRADING_DAYS_PER_YEAR = 252
NIFTY_50_SCHEME_CODE = 120716   # Nippon India Nifty 50 BeES (proxy for Nifty 50)
BENCHMARK_CODES = {
    "nifty50": 120716,          # Nifty 50 index fund
    "nifty_midcap": 145552,     # Nifty Midcap 150 index fund
    "nifty_smallcap": 122638,   # Nifty Smallcap 250 index fund
}


class FundMetricsScraper:
    """
    Fetch NAV history from MFAPI and compute comprehensive fund metrics.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MFHelper/1.0 (Fund Metrics Calculator)",
            "Accept": "application/json",
        })

        # Paths
        self.data_dir = Path(__file__).parent.parent / "data"
        self.fund_codes_file = self.data_dir / "moneycontrol_fund_codes.json"
        self.output_file = self.data_dir / "fund_metrics.json"
        self.mapping_file = self.data_dir / "fund_code_mapping.json"

        # State
        self.mc_funds = {}          # MoneyControl fund codes -> fund info
        self.mfapi_schemes = []     # All MFAPI scheme codes
        self.code_mapping = {}      # MC code -> MFAPI scheme code
        self.benchmark_navs = {}    # Benchmark NAV history (date -> nav)
        self.failed_funds = []

    # ------------------------------------------------------------------
    # Step 1: Load fund list and build MC -> MFAPI mapping
    # ------------------------------------------------------------------
    def load_fund_codes(self):
        """Load our 346 fund codes from moneycontrol_fund_codes.json"""
        print("\n" + "=" * 70)
        print("STEP 1: LOADING FUND LIST")
        print("=" * 70)

        if not self.fund_codes_file.exists():
            print(f"[ERROR] Fund codes file not found: {self.fund_codes_file}")
            return False

        with open(self.fund_codes_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.mc_funds = data.get("funds", {})
        print(f"[OK] Loaded {len(self.mc_funds)} funds from MoneyControl codes")
        return True

    def build_mfapi_mapping(self, force=False):
        """Build mapping from MoneyControl fund names to MFAPI scheme codes."""
        print("\n" + "=" * 70)
        print("STEP 2: BUILDING MFAPI SCHEME CODE MAPPING")
        print("=" * 70)

        # Check for cached mapping
        if self.mapping_file.exists() and not force:
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                cached = json.load(f)
            self.code_mapping = cached.get("mapping", {})
            if len(self.code_mapping) > 0:
                print(f"[OK] Loaded cached mapping: {len(self.code_mapping)} funds mapped")
                return True

        # Fetch all MFAPI schemes (one-time bulk download)
        print("[...] Fetching all MFAPI scheme list (~37K schemes)...")
        try:
            resp = self.session.get("https://api.mfapi.in/mf", timeout=30)
            if resp.status_code != 200:
                print(f"[ERROR] MFAPI returned {resp.status_code}")
                return False
            self.mfapi_schemes = resp.json()
            print(f"[OK] Got {len(self.mfapi_schemes)} schemes from MFAPI")
        except Exception as e:
            print(f"[ERROR] Failed to fetch MFAPI schemes: {e}")
            return False

        # Build lookup: lowercase name -> scheme code
        # Filter to Direct Growth plans only
        mfapi_lookup = {}
        for scheme in self.mfapi_schemes:
            name = scheme.get("schemeName", "")
            code = scheme.get("schemeCode")
            if code and name:
                # Normalize for matching
                norm = self._normalize_name(name)
                mfapi_lookup[norm] = {"code": code, "name": name}

        # Match each MC fund to MFAPI
        matched = 0
        for mc_code, fund_info in self.mc_funds.items():
            mc_name = fund_info["name"]
            mc_norm = self._normalize_name(mc_name)

            # Try exact match first
            if mc_norm in mfapi_lookup:
                self.code_mapping[mc_code] = {
                    "mfapi_code": mfapi_lookup[mc_norm]["code"],
                    "mfapi_name": mfapi_lookup[mc_norm]["name"],
                    "mc_name": mc_name,
                    "match_type": "exact",
                }
                matched += 1
                continue

            # Try fuzzy match: strip common suffixes and search
            best_match = self._fuzzy_match(mc_name, mfapi_lookup)
            if best_match:
                self.code_mapping[mc_code] = {
                    "mfapi_code": best_match["code"],
                    "mfapi_name": best_match["name"],
                    "mc_name": mc_name,
                    "match_type": "fuzzy",
                }
                matched += 1
            else:
                # Try MFAPI search API as fallback
                search_match = self._search_mfapi(mc_name)
                if search_match:
                    self.code_mapping[mc_code] = {
                        "mfapi_code": search_match["code"],
                        "mfapi_name": search_match["name"],
                        "mc_name": mc_name,
                        "match_type": "search",
                    }
                    matched += 1
                    time.sleep(0.3)  # Rate limit search API

        print(f"\n[OK] Mapped {matched}/{len(self.mc_funds)} funds ({matched/len(self.mc_funds)*100:.1f}%)")

        # Save mapping cache
        cache_data = {
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_mc_funds": len(self.mc_funds),
            "mapped": matched,
            "mapping": self.code_mapping,
        }
        with open(self.mapping_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved mapping to {self.mapping_file}")

        return True

    def _normalize_name(self, name):
        """Normalize fund name for matching."""
        n = name.lower().strip()
        # Remove common suffixes that differ between MC and MFAPI
        for suffix in [
            " - growth option", " option", " - growth", " growth",
            "- direct plan", " - direct plan", "direct plan",
            " plan", "(g)", "(growth)", "(div)", "(idcw)",
        ]:
            n = n.replace(suffix, "")
        # Normalize whitespace and special chars
        n = " ".join(n.split())
        n = n.replace("&", "and").replace("-", " ").replace("  ", " ").strip()
        return n

    def _fuzzy_match(self, mc_name, mfapi_lookup):
        """Try progressively looser matching."""
        mc_norm = self._normalize_name(mc_name)
        mc_words = set(mc_norm.split())

        best_score = 0
        best_match = None

        for norm_name, info in mfapi_lookup.items():
            mf_words = set(norm_name.split())
            # Jaccard similarity
            if not mc_words or not mf_words:
                continue
            intersection = mc_words & mf_words
            union = mc_words | mf_words
            score = len(intersection) / len(union)

            # Must have high similarity and share the key fund name words
            if score > 0.7 and score > best_score:
                # Verify it's the same AMC (first word usually is AMC name)
                mc_first = list(mc_words)[0] if mc_words else ""
                mf_first = list(mf_words)[0] if mf_words else ""
                if mc_first == mf_first or score > 0.85:
                    best_score = score
                    best_match = info

        return best_match

    def _search_mfapi(self, mc_name):
        """Use MFAPI search endpoint as fallback."""
        # Build search query from fund name
        search = mc_name.replace(" - Direct Plan - Growth", "").replace(" - Direct - Growth", "")
        search = search.strip()

        try:
            resp = self.session.get(
                f"https://api.mfapi.in/mf/search?q={search}",
                timeout=10,
            )
            if resp.status_code == 200:
                results = resp.json()
                # Filter for Direct Growth
                for r in results:
                    name = r.get("schemeName", "")
                    if "Direct" in name and "Growth" in name:
                        return {"code": r["schemeCode"], "name": name}
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # Step 2: Fetch benchmark NAV for Beta/Alpha calculations
    # ------------------------------------------------------------------
    def fetch_benchmark_nav(self):
        """Fetch Nifty 50 index fund NAV as benchmark."""
        print("\n" + "=" * 70)
        print("STEP 3: FETCHING BENCHMARK NAV (Nifty 50)")
        print("=" * 70)

        try:
            resp = self.session.get(
                f"https://api.mfapi.in/mf/{NIFTY_50_SCHEME_CODE}",
                timeout=30,
            )
            if resp.status_code != 200:
                print(f"[WARNING] Could not fetch benchmark NAV: HTTP {resp.status_code}")
                return False

            data = resp.json()
            nav_data = data.get("data", [])

            self.benchmark_navs = {}
            for point in nav_data:
                try:
                    date_str = point["date"]
                    nav = float(point["nav"])
                    self.benchmark_navs[date_str] = nav
                except (ValueError, KeyError):
                    continue

            print(f"[OK] Loaded {len(self.benchmark_navs)} benchmark NAV points")
            print(f"     Benchmark: {data.get('meta', {}).get('scheme_name', 'Unknown')}")
            return True
        except Exception as e:
            print(f"[WARNING] Benchmark fetch failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Step 3: Fetch NAV and compute metrics for each fund
    # ------------------------------------------------------------------
    def fetch_and_compute(self, mfapi_code, fund_info):
        """Fetch NAV history from MFAPI and compute all metrics."""
        try:
            resp = self.session.get(
                f"https://api.mfapi.in/mf/{mfapi_code}",
                timeout=30,
            )
            if resp.status_code != 200:
                return None

            data = resp.json()
            meta = data.get("meta", {})
            nav_data = data.get("data", [])

            if len(nav_data) < 30:
                return None

            # Parse NAV history (newest first from API, we reverse to oldest first)
            parsed_navs = []
            for point in nav_data:
                try:
                    d = datetime.strptime(point["date"], "%d-%m-%Y")
                    n = float(point["nav"])
                    parsed_navs.append((d, n))
                except (ValueError, KeyError):
                    continue

            parsed_navs.sort(key=lambda x: x[0])  # Oldest first

            if len(parsed_navs) < 30:
                return None

            latest_date = parsed_navs[-1][0]
            latest_nav = parsed_navs[-1][1]

            # Compute all metrics
            metrics = {
                "name": meta.get("scheme_name", fund_info.get("name", "")),
                "fund_house": meta.get("fund_house", ""),
                "category": meta.get("scheme_category", fund_info.get("category", "")),
                "scheme_code": meta.get("scheme_code", mfapi_code),
                "isin": meta.get("isin_growth", ""),
                "mc_code": fund_info.get("code", ""),
                "mc_category": fund_info.get("category", ""),
            }

            # NAV info
            metrics["nav"] = {
                "current": latest_nav,
                "date": latest_date.strftime("%Y-%m-%d"),
                "data_points": len(parsed_navs),
                "history_from": parsed_navs[0][0].strftime("%Y-%m-%d"),
            }

            # Returns
            metrics["returns"] = self._compute_returns(parsed_navs, latest_date, latest_nav)

            # Daily returns for risk metrics
            daily_returns = self._compute_daily_returns(parsed_navs)

            # Risk metrics (computed over different periods)
            metrics["risk"] = self._compute_risk_metrics(daily_returns, metrics["returns"])

            # Beta, Alpha, R-squared vs benchmark
            metrics["benchmark"] = self._compute_benchmark_metrics(parsed_navs, daily_returns)

            # Concentration / portfolio stats from our holdings data
            metrics["portfolio"] = self._get_portfolio_stats(fund_info)

            # Scrape metadata
            metrics["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return metrics

        except Exception as e:
            return None

    def _compute_returns(self, parsed_navs, latest_date, latest_nav):
        """Compute returns for various periods."""
        returns = {}

        periods = {
            "1w": 7, "1m": 30, "3m": 90, "6m": 180,
            "ytd": None,  # Special: from Jan 1 of current year
            "1y": 365, "2y": 730, "3y": 1095, "5y": 1825,
            "7y": 2555, "10y": 3650,
        }

        for period, days in periods.items():
            if period == "ytd":
                target_date = datetime(latest_date.year, 1, 1)
            else:
                target_date = latest_date - timedelta(days=days)

            # Find closest NAV to target date
            closest = min(parsed_navs, key=lambda x: abs(x[0] - target_date))

            # Only compute if we have data close enough to the target date
            date_diff = abs((closest[0] - target_date).days)
            if date_diff > 15:  # More than 15 days off means no data for this period
                continue

            if closest[1] <= 0:
                continue

            # Absolute return
            abs_return = ((latest_nav / closest[1]) - 1) * 100

            # CAGR for periods > 1 year
            actual_years = (latest_date - closest[0]).days / 365.25
            if actual_years >= 1:
                cagr = ((latest_nav / closest[1]) ** (1 / actual_years) - 1) * 100
                returns[period] = {
                    "absolute": round(abs_return, 2),
                    "cagr": round(cagr, 2),
                }
            else:
                returns[period] = {
                    "absolute": round(abs_return, 2),
                }

        return returns

    def _compute_daily_returns(self, parsed_navs):
        """Compute daily return series."""
        daily = []
        for i in range(1, len(parsed_navs)):
            prev_nav = parsed_navs[i - 1][1]
            curr_nav = parsed_navs[i][1]
            if prev_nav > 0:
                daily.append({
                    "date": parsed_navs[i][0],
                    "return": (curr_nav / prev_nav) - 1,
                })
        return daily

    def _compute_risk_metrics(self, daily_returns, returns_data):
        """Compute risk metrics for 1Y and 3Y periods."""
        risk = {}

        for period, days in [("1y", 252), ("3y", 756)]:
            recent = daily_returns[-days:] if len(daily_returns) >= days else daily_returns
            if len(recent) < 30:
                continue

            rets = [d["return"] for d in recent]

            # Standard Deviation (annualized)
            std_daily = statistics.stdev(rets) if len(rets) > 1 else 0
            std_annual = std_daily * math.sqrt(TRADING_DAYS_PER_YEAR) * 100

            # Downside deviation (for Sortino)
            neg_rets = [r for r in rets if r < 0]
            downside_dev_daily = statistics.stdev(neg_rets) if len(neg_rets) > 1 else 0
            downside_dev_annual = downside_dev_daily * math.sqrt(TRADING_DAYS_PER_YEAR) * 100

            # Annualized return from daily returns
            total_ret = 1
            for r in rets:
                total_ret *= (1 + r)
            ann_years = len(rets) / TRADING_DAYS_PER_YEAR
            annualized_return = ((total_ret ** (1 / ann_years)) - 1) * 100 if ann_years > 0 else 0

            # Sharpe Ratio
            sharpe = (annualized_return - RISK_FREE_RATE) / std_annual if std_annual > 0 else 0

            # Sortino Ratio
            sortino = (annualized_return - RISK_FREE_RATE) / downside_dev_annual if downside_dev_annual > 0 else 0

            # Max Drawdown
            peak = 1
            max_dd = 0
            cumulative = 1
            for r in rets:
                cumulative *= (1 + r)
                if cumulative > peak:
                    peak = cumulative
                dd = (peak - cumulative) / peak * 100
                if dd > max_dd:
                    max_dd = dd

            # VaR (95%)  - parametric
            mean_daily = statistics.mean(rets) if rets else 0
            var_95 = -(mean_daily - 1.645 * std_daily) * 100

            risk[period] = {
                "std_dev": round(std_annual, 2),
                "sharpe": round(sharpe, 2),
                "sortino": round(sortino, 2),
                "max_drawdown": round(max_dd, 2),
                "var_95": round(var_95, 2),
                "annualized_return": round(annualized_return, 2),
                "trading_days": len(rets),
            }

        return risk

    def _compute_benchmark_metrics(self, parsed_navs, daily_returns):
        """Compute Beta, Alpha, R-squared against Nifty 50."""
        if not self.benchmark_navs or len(daily_returns) < 60:
            return {"available": False}

        # Align fund daily returns with benchmark daily returns
        fund_rets = []
        bench_rets = []

        benchmark_dates = sorted(self.benchmark_navs.keys(),
                                 key=lambda d: datetime.strptime(d, "%d-%m-%Y"))

        # Build benchmark daily returns lookup
        bench_daily = {}
        prev_nav = None
        for date_str in benchmark_dates:
            nav = self.benchmark_navs[date_str]
            if prev_nav and prev_nav > 0:
                bench_daily[date_str] = (nav / prev_nav) - 1
            prev_nav = nav

        # Match dates (use last 3 years of data)
        for dr in daily_returns[-756:]:
            date_str = dr["date"].strftime("%d-%m-%Y")
            if date_str in bench_daily:
                fund_rets.append(dr["return"])
                bench_rets.append(bench_daily[date_str])

        if len(fund_rets) < 30:
            return {"available": False, "reason": "Insufficient overlapping dates"}

        # Beta = Cov(fund, bench) / Var(bench)
        n = len(fund_rets)
        mean_f = sum(fund_rets) / n
        mean_b = sum(bench_rets) / n

        cov = sum((f - mean_f) * (b - mean_b) for f, b in zip(fund_rets, bench_rets)) / (n - 1)
        var_b = sum((b - mean_b) ** 2 for b in bench_rets) / (n - 1)

        beta = cov / var_b if var_b > 0 else 1.0

        # Alpha (Jensen's Alpha) = annualized
        ann_fund = ((1 + mean_f) ** TRADING_DAYS_PER_YEAR - 1) * 100
        ann_bench = ((1 + mean_b) ** TRADING_DAYS_PER_YEAR - 1) * 100
        alpha = ann_fund - (RISK_FREE_RATE + beta * (ann_bench - RISK_FREE_RATE))

        # R-squared
        ss_res = sum((f - mean_f - beta * (b - mean_b)) ** 2 for f, b in zip(fund_rets, bench_rets))
        ss_tot = sum((f - mean_f) ** 2 for f in fund_rets)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Treynor Ratio
        treynor = (ann_fund - RISK_FREE_RATE) / beta if beta != 0 else 0

        # Information Ratio = (fund return - bench return) / tracking error
        excess = [f - b for f, b in zip(fund_rets, bench_rets)]
        tracking_error = statistics.stdev(excess) * math.sqrt(TRADING_DAYS_PER_YEAR) * 100 if len(excess) > 1 else 0
        info_ratio = (ann_fund - ann_bench) / tracking_error if tracking_error > 0 else 0

        # Up/Down capture
        up_fund = [f for f, b in zip(fund_rets, bench_rets) if b > 0]
        up_bench = [b for b in bench_rets if b > 0]
        down_fund = [f for f, b in zip(fund_rets, bench_rets) if b < 0]
        down_bench = [b for b in bench_rets if b < 0]

        up_capture = (sum(up_fund) / sum(up_bench) * 100) if up_bench and sum(up_bench) != 0 else 100
        down_capture = (sum(down_fund) / sum(down_bench) * 100) if down_bench and sum(down_bench) != 0 else 100

        return {
            "available": True,
            "benchmark": "Nifty 50",
            "beta": round(beta, 2),
            "alpha": round(alpha, 2),
            "r_squared": round(r_squared, 4),
            "treynor": round(treynor, 2),
            "info_ratio": round(info_ratio, 2),
            "tracking_error": round(tracking_error, 2),
            "up_capture": round(up_capture, 2),
            "down_capture": round(down_capture, 2),
            "overlapping_days": len(fund_rets),
        }

    def _get_portfolio_stats(self, fund_info):
        """Pull portfolio stats from our existing fund_holdings.json if available."""
        holdings_file = self.data_dir / "fund_holdings.json"
        if not holdings_file.exists():
            return {}

        try:
            with open(holdings_file, "r", encoding="utf-8", errors="replace") as f:
                holdings_data = json.load(f)

            funds = holdings_data.get("funds", {})
            # Try to find this fund by name matching
            mc_name = fund_info.get("name", "")
            fund_key = mc_name.lower().replace(" ", "-")

            # Look through funds for a match
            for key, fund in funds.items():
                if key == fund_key or fund.get("fund_code") == fund_info.get("code"):
                    holdings = fund.get("holdings", [])
                    if not holdings:
                        return {}

                    total_weight = sum(h.get("weight", 0) for h in holdings)
                    sectors = defaultdict(float)
                    for h in holdings:
                        sector = h.get("sector", "Unknown")
                        sectors[sector] += h.get("weight", 0)

                    top_sectors = sorted(sectors.items(), key=lambda x: -x[1])[:5]
                    top5_weight = sum(h.get("weight", 0) for h in sorted(holdings, key=lambda x: -x.get("weight", 0))[:5])
                    top10_weight = sum(h.get("weight", 0) for h in sorted(holdings, key=lambda x: -x.get("weight", 0))[:10])

                    return {
                        "num_stocks": len(holdings),
                        "total_weight": round(total_weight, 2),
                        "top5_weight": round(top5_weight, 2),
                        "top10_weight": round(top10_weight, 2),
                        "top_sectors": [{"sector": s, "weight": round(w, 2)} for s, w in top_sectors],
                    }
        except Exception:
            pass
        return {}

    # ------------------------------------------------------------------
    # Main scrape loop
    # ------------------------------------------------------------------
    def scrape(self, limit=None, force=False, fund_code=None):
        """Main entry point: scrape metrics for all (or selected) funds."""
        print("\n" + "=" * 70)
        print("FUND METRICS SCRAPER")
        print("Computing risk/return metrics from MFAPI NAV history")
        print("=" * 70)

        # Step 1: Load fund list
        if not self.load_fund_codes():
            return False

        # Step 2: Build MFAPI mapping
        if not self.build_mfapi_mapping(force=force):
            return False

        # Step 3: Fetch benchmark
        self.fetch_benchmark_nav()
        time.sleep(1)

        # Step 4: Load existing metrics (for skip logic)
        existing_metrics = {}
        if self.output_file.exists() and not force:
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                existing_metrics = existing_data.get("funds", {})
                print(f"\n[OK] Found {len(existing_metrics)} existing fund metrics")
            except Exception:
                pass

        # Step 5: Determine which funds to process
        if fund_code:
            # Single fund mode
            if fund_code in self.code_mapping:
                funds_to_process = {fund_code: self.mc_funds.get(fund_code, {})}
            else:
                print(f"[ERROR] Fund code {fund_code} not found in mapping")
                return False
        else:
            funds_to_process = {}
            for mc_code, fund_info in self.mc_funds.items():
                if mc_code not in self.code_mapping:
                    continue
                if mc_code in existing_metrics and not force:
                    continue
                funds_to_process[mc_code] = fund_info

        if limit:
            codes = list(funds_to_process.keys())[:limit]
            funds_to_process = {c: funds_to_process[c] for c in codes}

        total = len(funds_to_process)
        print(f"\n{'=' * 70}")
        print(f"STEP 4: COMPUTING METRICS FOR {total} FUNDS")
        print(f"{'=' * 70}")

        if total == 0:
            print("[OK] All funds already have metrics. Use --force to recompute.")
            return True

        print(f"Estimated time: ~{total * 1.5 / 60:.1f} minutes ({total} funds x ~1.5s)")

        # Process each fund
        computed_metrics = dict(existing_metrics)  # Start with existing
        success = 0
        failed = 0

        for idx, (mc_code, fund_info) in enumerate(funds_to_process.items(), 1):
            mapping = self.code_mapping.get(mc_code)
            if not mapping:
                continue

            mfapi_code = mapping["mfapi_code"]
            fund_name = fund_info.get("name", mc_code)

            progress = f"[{idx}/{total}]"
            print(f"\n{progress} {fund_name[:60]}...")

            metrics = self.fetch_and_compute(mfapi_code, fund_info)

            if metrics:
                computed_metrics[mc_code] = metrics
                success += 1

                # Show key metrics
                risk_1y = metrics.get("risk", {}).get("1y", {})
                ret_1y = metrics.get("returns", {}).get("1y", {})
                bench = metrics.get("benchmark", {})

                summary_parts = []
                if ret_1y:
                    summary_parts.append(f"1Y: {ret_1y.get('absolute', '?')}%")
                if risk_1y:
                    summary_parts.append(f"Sharpe: {risk_1y.get('sharpe', '?')}")
                    summary_parts.append(f"StdDev: {risk_1y.get('std_dev', '?')}%")
                if bench.get("available"):
                    summary_parts.append(f"Beta: {bench.get('beta', '?')}")
                    summary_parts.append(f"Alpha: {bench.get('alpha', '?')}")

                print(f"  [OK] {' | '.join(summary_parts)}")
            else:
                failed += 1
                self.failed_funds.append({"code": mc_code, "name": fund_name})
                print(f"  [FAIL] Could not compute metrics")

            # Save progress every 25 funds
            if idx % 25 == 0:
                self._save_metrics(computed_metrics)
                print(f"\n  [SAVE] Progress saved: {success} computed, {failed} failed")

            # Rate limiting
            time.sleep(1)

        # Final save
        self._save_metrics(computed_metrics)

        # Summary
        print("\n" + "=" * 70)
        print("SCRAPING SUMMARY")
        print("=" * 70)
        print(f"  Successfully computed: {success} funds")
        print(f"  Failed: {failed} funds")
        print(f"  Total in output: {len(computed_metrics)} funds")
        print(f"  Output: {self.output_file}")

        if self.failed_funds:
            print(f"\n  Failed funds:")
            for f in self.failed_funds[:10]:
                print(f"    - {f['name']} ({f['code']})")
            if len(self.failed_funds) > 10:
                print(f"    ... and {len(self.failed_funds) - 10} more")

        return True

    def _save_metrics(self, metrics):
        """Save metrics to JSON file."""
        output = {
            "version": "2026-02",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "MFAPI NAV History + Computed Metrics",
            "risk_free_rate": RISK_FREE_RATE,
            "benchmark": "Nifty 50 (via index fund proxy)",
            "total_funds": len(metrics),
            "funds": metrics,
        }

        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)


def main():
    parser = argparse.ArgumentParser(
        description="Compute fund risk/return metrics from MFAPI NAV history"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit number of funds to process (default: all)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Recompute metrics even if already exists"
    )
    parser.add_argument(
        "--fund-code", type=str, default=None,
        help="Process a single fund by MoneyControl code (e.g., MHD1161)"
    )
    parser.add_argument(
        "--rebuild-mapping", action="store_true",
        help="Rebuild the MoneyControl -> MFAPI code mapping"
    )
    args = parser.parse_args()

    scraper = FundMetricsScraper()
    scraper.scrape(
        limit=args.limit,
        force=args.force or args.rebuild_mapping,
        fund_code=args.fund_code,
    )

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. View metrics: backend/data/fund_metrics.json")
    print("2. Load to DB:   python backend/scripts/load_fund_metrics_to_db.py")
    print("3. API test:     GET /api/funds/metrics?name=HDFC%20Flexi")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
