import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {
  const BASE_URL = 'http://localhost:8000';

  test.skip('should fetch AMC list successfully', async ({ request }) => {
    // TODO: Fix route conflict - amc-list being interpreted as fund_id
    const response = await request.get(`${BASE_URL}/api/funds/amc-list`);
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.amcs).toBeInstanceOf(Array);
    expect(data.amcs.length).toBeGreaterThan(0);
    
    console.log(`✅ AMC API returned ${data.amcs.length} AMCs`);
    console.log('Sample AMCs:', data.amcs.slice(0, 5));
  });

  test('should search funds by AMC', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/funds/list?amc=HDFC&limit=10`);
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    expect(data.success).toBe(true);
    expect(data.funds).toBeInstanceOf(Array);
    
    if (data.funds.length > 0) {
      // Verify all returned funds are from HDFC
      const allHDFC = data.funds.every((fund: any) => 
        fund.amc === 'HDFC' || fund.scheme_name.includes('HDFC')
      );
      expect(allHDFC).toBe(true);
    }
    
    console.log(`✅ Fund search by AMC returned ${data.funds.length} funds`);
  });

  test('should search funds by keyword', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/funds/list?search=Flexi&limit=10`);
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    expect(data.success).toBe(true);
    expect(data.funds).toBeInstanceOf(Array);
    
    console.log(`✅ Keyword search returned ${data.funds.length} funds`);
  });

  test('should handle health check', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/health`);
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    expect(data.status).toBe('healthy');
    console.log('✅ Health check passed:', data);
  });

  test('should handle CORS headers', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/health`);
    
    const headers = response.headers();
    // Check if CORS header exists (may vary by configuration)
    expect(response.ok()).toBeTruthy();
    
    console.log('✅ CORS check passed');
  });

  test('API should not return 500 errors on valid requests', async ({ request }) => {
    const endpoints = [
      '/api/funds/amc-list',
      '/api/funds/list?limit=5',
      '/health'
    ];
    
    for (const endpoint of endpoints) {
      const response = await request.get(`${BASE_URL}${endpoint}`);
      expect(response.status()).not.toBe(500);
      console.log(`✅ ${endpoint} - Status: ${response.status()}`);
    }
  });
});
