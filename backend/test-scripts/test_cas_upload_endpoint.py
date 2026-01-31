"""
Test CAS upload endpoint with real file
"""
import requests
import json

# API endpoint
BASE_URL = "http://localhost:8000"
CAS_FILE = r"C:\Users\mahchi01\Downloads\KFINTECH_97924150102202603102380252686267905.pdf"
PASSWORD = "Mahesh@1234"

# First, login to get token
def login():
    """Login to get auth token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": "demo@mfhelper.com",
            "password": "Demo@123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code}")
        print(response.json())
        return None

# Upload CAS
def upload_cas(token):
    """Upload CAS PDF"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open(CAS_FILE, 'rb') as f:
        files = {
            'file': ('cas.pdf', f, 'application/pdf')
        }
        data = {
            'password': PASSWORD,
            'save_to_db': 'true'
        }
        
        print(f"\nUploading CAS file: {CAS_FILE}")
        print(f"Password: {PASSWORD}")
        print(f"Endpoint: {BASE_URL}/api/upload/cas\n")
        
        response = requests.post(
            f"{BASE_URL}/api/upload/cas",
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("=" * 80)
            print("✓ CAS UPLOAD SUCCESSFUL!")
            print("=" * 80)
            print(f"\nFile Type: {result['file_info']['file_type']}")
            print(f"Statement Period: {result['file_info']['statement_period']['from']} to {result['file_info']['statement_period']['to']}")
            
            print(f"\n📊 PORTFOLIO SUMMARY:")
            summary = result['summary']
            print(f"   Total Folios: {summary['total_folios']}")
            print(f"   Total Schemes: {summary['total_schemes']}")
            print(f"   Total Invested: ₹{summary['total_invested']:,.2f}")
            print(f"   Current Value: ₹{summary['current_value']:,.2f}")
            print(f"   Total Gain/Loss: ₹{summary['total_gain_loss']:,.2f}")
            print(f"   Overall Return: {summary['overall_return_pct']}%")
            
            if 'portfolio_id' in result:
                print(f"\n✓ Saved to database with Portfolio ID: {result['portfolio_id']}")
            
            print(f"\n📁 TOP 5 FOLIOS:")
            for i, folio in enumerate(result['folios'][:5], 1):
                print(f"\n{i}. {folio['amc']}")
                print(f"   Folio: {folio['folio_number']}")
                print(f"   Schemes: {folio['schemes_count']}")
                print(f"   Value: ₹{folio['total_value']:,.2f}")
                print(f"   Gain: ₹{folio['gain_loss']:,.2f}")
            
            # Save full response
            with open('cas_upload_response.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Full response saved to: cas_upload_response.json")
            
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(response.json())

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING CAS UPLOAD ENDPOINT")
    print("=" * 80)
    
    # Step 1: Login
    print("\n1. Logging in...")
    token = login()
    if not token:
        print("✗ Cannot proceed without login")
        exit(1)
    print("✓ Login successful")
    
    # Step 2: Upload CAS
    print("\n2. Uploading CAS...")
    upload_cas(token)
