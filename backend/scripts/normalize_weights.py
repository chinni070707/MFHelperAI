"""Quick check why weights > 110% for 3 funds, then normalize"""
import json

with open("data/fund_holdings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

problem_funds = [
    "hdfc-mid-cap-opportunities-fund",
    "mirae-asset-emerging-bluechip-fund",
    "kotak-equity-opportunities-fund",
]

for key in problem_funds:
    fund = data["funds"][key]
    holdings = fund["holdings"]
    total = sum(h["weight"] for h in holdings)
    print(f"\n{key}: total={total:.1f}%, {len(holdings)} holdings")
    if total > 110:
        # Normalize weights to sum to 100
        factor = 100.0 / total
        for h in holdings:
            h["weight"] = round(h["weight"] * factor, 2)
        new_total = sum(h["weight"] for h in holdings)
        print(f"  Normalized: {total:.1f}% -> {new_total:.1f}%")

with open("data/fund_holdings.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nDone. Saved.")
