"""
Manual API Testing Script
Simple script to test new endpoints without database setup
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_result(test_name, response):
    """Print test result"""
    status = "✅ PASS" if response.status_code in [200, 201] else "❌ FAIL"
    print(f"\n{status} {test_name}")
    print(f"Status: {response.status_code}")
    if response.text:
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
        except:
            print(f"Response: {response.text[:200]}...")

def test_health():
    """Test health endpoint"""
    print("\n=== HEALTH CHECK ===")
    response = requests.get(f"{BASE_URL}/api/health/")
    print_result("Health Check", response)

def test_demo_portfolio():
    """Test demo portfolio endpoint"""
    print("\n=== DEMO PORTFOLIO ===")
    
    # Try to get demo portfolio
    response = requests.get(f"{BASE_URL}/api/demo/portfolio")
    print_result("Get Demo Portfolio", response)

def test_funds_list():
    """Test funds list endpoint"""
    print("\n=== FUNDS LIST ===")
    
    # Get all funds
    response = requests.get(f"{BASE_URL}/api/funds/list?limit=5")
    print_result("Get Funds List", response)
    
    # Search for HDFC funds
    response = requests.get(f"{BASE_URL}/api/funds/list?search=HDFC&limit=5")
    print_result("Search Funds (HDFC)", response)
    
    # Get categories
    response = requests.get(f"{BASE_URL}/api/funds/categories")
    print_result("Get Fund Categories", response)

def test_lead_capture():
    """Test lead capture endpoint"""
    print("\n=== LEAD CAPTURE ===")
    
    data = {
        "email": f"test_{int(datetime.now().timestamp())}@example.com",
        "source": "test-script"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/leads/capture",
        json=data
    )
    print_result("Capture Lead", response)

def test_auth_endpoints():
    """Test auth endpoints structure (without actual signup)"""
    print("\n=== AUTH ENDPOINTS ===")
    
    # These will fail without valid data, but we can see if routes exist
    response = requests.post(f"{BASE_URL}/api/auth/register", json={})
    print(f"Register endpoint: {'exists ✓' if response.status_code != 404 else 'missing ✗'}")
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json={})
    print(f"Login endpoint: {'exists ✓' if response.status_code != 404 else 'missing ✗'}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("MANUAL API TESTING - NEW FEATURES")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test basic health
        test_health()
        
        # Test new features
        test_demo_portfolio()
        test_funds_list()
        test_lead_capture()
        test_auth_endpoints()
        
        print("\n" + "=" * 60)
        print("TESTING COMPLETE")
        print("=" * 60)
        print("\nNote: Some endpoints may fail due to missing database setup")
        print("Run database migrations first: alembic upgrade head")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print(f"Make sure server is running at {BASE_URL}")
        print("Start with: cd backend && python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
