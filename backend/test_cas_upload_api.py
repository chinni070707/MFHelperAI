"""
Test CAS upload through the actual API endpoint 
"""
import sys
import requests
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
CAS_PDF_PATH = r"c:\Users\mahchi01\Downloads\CAS\KFINTECH_97924150102202603102380252686267905.pdf"
PASSWORD = "Mahesh@1234"

print("🚀 Testing CAS Upload via API")
print("=" * 80)

# Check if backend is running
try:
    response = requests.get(f"{API_URL}/api/health", timeout=5)
    print(f"✅ Backend is running at {API_URL}")
except requests.exceptions.ConnectionError:
    print(f"❌ Backend is not running at {API_URL}")
    print("💡 Start the backend with: cd backend && python -m uvicorn app.main:app --reload")
    sys.exit(1)

# Check if file exists
if not Path(CAS_PDF_PATH).exists():
    print(f"❌ CAS file not found: {CAS_PDF_PATH}")
    sys.exit(1)

print(f"📄 CAS file: {CAS_PDF_PATH}")
print(f"🔐 Password: {PASSWORD}")
print()

# First, register/login to get auth token
print("🔑 Getting authentication token...")
try:
    # Try to login with existing test credentials
    test_users = [
        {"email": "test@example.com", "password": "Test@1234"},
        {"email": "mahesh@test.com", "password": "Test@1234"},
        {"email": "admin@test.com", "password": "Admin@1234"},
    ]
    
    token = None
    for user in test_users:
        try:
            print(f"   Trying to login as {user['email']}...")
            login_response = requests.post(
                f"{API_URL}/api/auth/login",
                json=user
            )
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                print(f"   ✅ Logged in as {user['email']}")
                break
        except Exception as e:
            continue
    
    if not token:
        print("   ⚠️  No existing test user found. Please use frontend to create a user first.")
        print("   💡 Or run: curl -X POST http://localhost:8000/api/auth/register -H 'Content-Type: application/json' -d '{\"name\":\"Test\",\"email\":\"test@example.com\",\"password\":\"Test@1234\"}'")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Auth error: {e}")
    sys.exit(1)

print()

# Now upload the CAS file
print("📤 Uploading CAS file...")
try:
    with open(CAS_PDF_PATH, 'rb') as f:
        files = {'file': ('cas.pdf', f, 'application/pdf')}
        data = {'password': PASSWORD}
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(
            f"{API_URL}/api/upload/cas",
            files=files,
            data=data,
            headers=headers
        )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Upload successful!")
        print()
        print("   📊 Summary:")
        print(f"      Holdings imported: {result.get('holdings_count', 0)}")
        print(f"      Total current value: ₹{result.get('total_current_value', 0):,.2f}")
        print(f"      Total invested: ₹{result.get('total_invested', 0):,.2f}")
        print(f"      Total gain/loss: ₹{result.get('total_gain_loss', 0):,.2f}")
    else:
        print(f"   ❌ Upload failed!")
        print(f"   Response: {response.text}")
        
        # Try to get more details
        try:
            error_data = response.json()
            print(f"   Error detail: {error_data.get('detail', 'No detail')}")
        except:
            pass
            
except Exception as e:
    print(f"   ❌ Upload error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("✅ Test complete")
