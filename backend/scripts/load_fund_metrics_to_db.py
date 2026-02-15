"""
Load Fund Metrics from JSON into FundMaster Database Table

Reads fund_metrics.json and updates FundMaster records with computed
risk/return metrics (sharpe, sortino, beta, alpha, etc.)

Usage:
    PYTHONPATH=backend python backend/scripts/load_fund_metrics_to_db.py
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.models import FundMaster


def load_metrics():
    """Load fund_metrics.json into FundMaster table."""
    metrics_file = Path(__file__).parent.parent / "data" / "fund_metrics.json"
    
    if not metrics_file.exists():
        print("[ERROR] fund_metrics.json not found. Run scrape_fund_metrics.py first.")
        return
    
    with open(metrics_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    funds = data.get("funds", {})
    print(f"\n[OK] Loaded {len(funds)} funds from fund_metrics.json")
    print(f"     Last updated: {data.get('last_updated')}")
    
    db = SessionLocal()
    
    try:
        updated = 0
        not_found = 0
        created = 0
        
        for mc_code, metrics in funds.items():
            fund_name = metrics.get("name", "")
            scheme_code = str(metrics.get("scheme_code", ""))
            isin = metrics.get("isin", "")
            
            # Try to find existing FundMaster record
            fund = None
            
            # 1. By mc_code (fastest if already linked)
            if mc_code:
                fund = db.query(FundMaster).filter(
                    FundMaster.mc_code == mc_code
                ).first()
            
            # 2. By ISIN (most reliable cross-system identifier)
            if not fund and isin:
                fund = db.query(FundMaster).filter(
                    FundMaster.isin == isin
                ).first()
            
            # 3. By scheme_code (may differ between systems)
            if not fund and scheme_code:
                fund = db.query(FundMaster).filter(
                    FundMaster.scheme_code == scheme_code
                ).first()
            
            # 4. By name matching - try multiple variations
            if not fund and fund_name:
                # Try exact match
                fund = db.query(FundMaster).filter(
                    FundMaster.scheme_name == fund_name
                ).first()
                
                # Try without common suffixes
                if not fund:
                    for suffix in [" - Growth Option", " Option", " Growth"]:
                        clean = fund_name.replace(suffix, "").strip()
                        if clean != fund_name:
                            fund = db.query(FundMaster).filter(
                                FundMaster.scheme_name.ilike(f"%{clean}%")
                            ).first()
                            if fund:
                                break
                
                # Try core name (first 30 chars)
                if not fund and len(fund_name) > 20:
                    # Extract AMC + fund type  
                    core = fund_name.split(" - ")[0].strip() if " - " in fund_name else fund_name[:30]
                    candidates = db.query(FundMaster).filter(
                        FundMaster.scheme_name.ilike(f"%{core}%"),
                        FundMaster.plan_type == "Direct"
                    ).all()
                    if len(candidates) == 1:
                        fund = candidates[0]
                    elif candidates:
                        # Pick the one with "Growth" in name
                        for c in candidates:
                            if "Growth" in (c.scheme_name or ""):
                                fund = c
                                break
            
            if not fund:
                # Don't create new records with potentially conflicting scheme_codes
                # Just log it
                not_found += 1
                continue
            
            # Update metrics fields
            risk_3y = metrics.get("risk", {}).get("3y", {})
            risk_1y = metrics.get("risk", {}).get("1y", {})
            benchmark = metrics.get("benchmark", {})
            returns = metrics.get("returns", {})
            portfolio = metrics.get("portfolio", {})
            nav = metrics.get("nav", {})
            
            # Use 3Y risk metrics if available, otherwise 1Y
            risk = risk_3y if risk_3y else risk_1y
            
            fund.mc_code = mc_code
            fund.sharpe_ratio = risk.get("sharpe")
            fund.sortino_ratio = risk.get("sortino")
            fund.std_dev = risk.get("std_dev")
            fund.max_drawdown = risk.get("max_drawdown")
            
            if benchmark.get("available"):
                fund.beta = benchmark.get("beta")
                fund.alpha = benchmark.get("alpha")
                fund.r_squared = benchmark.get("r_squared")
                fund.treynor_ratio = benchmark.get("treynor")
                fund.info_ratio = benchmark.get("info_ratio")
                fund.up_capture = benchmark.get("up_capture")
                fund.down_capture = benchmark.get("down_capture")
                fund.tracking_error = benchmark.get("tracking_error")
            
            # Returns
            if returns.get("1y"):
                fund.one_year_return = returns["1y"].get("absolute")
            if returns.get("3y"):
                fund.three_year_return = returns["3y"].get("cagr", returns["3y"].get("absolute"))
            if returns.get("5y"):
                fund.five_year_return = returns["5y"].get("cagr", returns["5y"].get("absolute"))
            
            # Portfolio
            fund.num_stocks = portfolio.get("num_stocks")
            fund.top5_weight = portfolio.get("top5_weight")
            fund.top10_weight = portfolio.get("top10_weight")
            
            # NAV
            fund.current_nav = nav.get("current")
            
            # Timestamp
            fund.metrics_updated_at = datetime.now()
            
            updated += 1
        
        db.commit()
        
        print(f"\n{'=' * 50}")
        print(f"DB UPDATE SUMMARY")
        print(f"{'=' * 50}")
        print(f"  Updated: {updated} fund records")
        print(f"  Created: {created} new records")
        print(f"  Not found: {not_found}")
        print(f"{'=' * 50}\n")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Database update failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_metrics()
