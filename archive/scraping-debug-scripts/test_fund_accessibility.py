"""
Test which funds actually have portfolio data on MoneyControl
Tests all 346 fund codes to see which ones return valid data vs 403 errors
"""
import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import time

def test_fund_accessibility(fund_code, fund_url, fund_name):
    """Quick test if fund has portfolio data"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        response = requests.get(fund_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Check if it actually has portfolio table
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            for table in tables:
                header_row = table.find('tr')
                if header_row:
                    headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
                    if 'Stock Invested in' in headers:
                        return 'SUCCESS', None
            return 'NO_TABLE', 'Page loads but no portfolio table found'
        elif response.status_code == 403:
            return 'FORBIDDEN', '403 Forbidden'
        elif response.status_code == 404:
            return 'NOT_FOUND', '404 Not Found'
        else:
            return 'ERROR', f'HTTP {response.status_code}'
            
    except requests.Timeout:
        return 'TIMEOUT', 'Request timeout'
    except Exception as e:
        return 'ERROR', str(e)[:50]

def main(quick_mode=False):
    # Load fund codes
    data_dir = Path(__file__).parent.parent / 'data'
    fund_codes_file = data_dir / 'moneycontrol_fund_codes.json'
    
    print("\n" + "="*80)
    print("TESTING MONEYCONTROL FUND ACCESSIBILITY")
    print("="*80)
    
    with open(fund_codes_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    funds_dict = data.get('funds', {})
    
    # Limit to first 50 if quick mode
    if quick_mode:
        funds_dict = dict(list(funds_dict.items())[:50])
        print("\n⚡ QUICK MODE: Testing first 50 funds only")
    
    total = len(funds_dict)
    
    print(f"\nTotal funds to test: {total}")
    print(f"Estimated time: {total * 2 / 60:.1f} minutes")
    print("\nTesting... (this will take a while)\n")
    
    results = {
        'SUCCESS': [],
        'FORBIDDEN': [],
        'NOT_FOUND': [],
        'NO_TABLE': [],
        'TIMEOUT': [],
        'ERROR': []
    }
    
    tested = 0
    for code, fund_info in funds_dict.items():
        tested += 1
        url = f"https://www.moneycontrol.com/mutual-funds/{fund_info['slug']}/portfolio-holdings/{code}"
        
        status, error = test_fund_accessibility(code, url, fund_info['name'])
        results[status].append({
            'code': code,
            'name': fund_info['name'],
            'category': fund_info.get('category', 'Unknown'),
            'error': error
        })
        
        # Progress update every 10 funds
        if tested % 10 == 0:
            success_count = len(results['SUCCESS'])
            print(f"[{tested}/{total}] Tested... {success_count} working so far")
        
        # Rate limiting
        time.sleep(2)
    
    # Summary
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    success_count = len(results['SUCCESS'])
    forbidden_count = len(results['FORBIDDEN'])
    
    print(f"\n✅ SUCCESS (Have portfolio data): {success_count} funds")
    print(f"❌ FORBIDDEN (403 error): {forbidden_count} funds")
    print(f"❌ NOT FOUND (404 error): {len(results['NOT_FOUND'])} funds")
    print(f"⚠️  NO TABLE (Page loads but no portfolio): {len(results['NO_TABLE'])} funds")
    print(f"⏱️  TIMEOUT: {len(results['TIMEOUT'])} funds")
    print(f"💥 ERROR (Other): {len(results['ERROR'])} funds")
    
    print(f"\n📊 Success Rate: {success_count/total*100:.1f}%")
    
    # Save detailed results
    output_file = data_dir / 'moneycontrol_accessibility_test.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': '2026-02-14',
            'total_tested': total,
            'summary': {
                'success': success_count,
                'forbidden': forbidden_count,
                'not_found': len(results['NOT_FOUND']),
                'no_table': len(results['NO_TABLE']),
                'timeout': len(results['TIMEOUT']),
                'error': len(results['ERROR'])
            },
            'details': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Show some examples of successful funds
    if results['SUCCESS']:
        print(f"\n✅ Sample of working funds:")
        for fund in results['SUCCESS'][:10]:
            print(f"   - {fund['name']} ({fund['code']})")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='Test only first 50 funds')
    args = parser.parse_args()
    
    main(quick_mode=args.quick)
