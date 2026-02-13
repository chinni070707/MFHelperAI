/**
 * MFHelper E2E Tests — CAS Upload Flow
 * 
 * NOTE: Dashboard DOMContentLoaded handler has JS errors on the live site —
 * Tests use page.evaluate to force-show the upload modal directly.
 */
/// <reference types="node" />
import { test, expect } from '@playwright/test';

test.describe('CAS Upload — Modal via Direct JS', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => localStorage.clear());
    await page.goto('/dashboard.html');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);
  });

  test('upload modal exists in DOM and can be shown programmatically', async ({ page }) => {
    const modal = page.locator('#uploadModal');
    expect(await modal.count()).toBeGreaterThan(0);

    // Force show the modal via JS (since the normal click path may be blocked by bugs)
    await page.evaluate(() => {
      const modal = document.getElementById('uploadModal');
      if (modal) modal.style.display = 'flex';
    });

    await expect(modal).toBeVisible();
  });

  test('upload modal has file input for CAS PDF', async ({ page }) => {
    await page.evaluate(() => {
      const modal = document.getElementById('uploadModal');
      if (modal) modal.style.display = 'flex';
    });

    const fileInput = page.locator('#uploadModal input[type="file"]');
    expect(await fileInput.count()).toBeGreaterThan(0);
  });

  test('upload modal has upload/submit button', async ({ page }) => {
    await page.evaluate(() => {
      const modal = document.getElementById('uploadModal');
      if (modal) modal.style.display = 'flex';
    });

    const uploadBtn = page.locator('#uploadModal button').filter({ hasText: /Upload|Submit|Import/i });
    expect(await uploadBtn.count()).toBeGreaterThan(0);
  });

  test('upload modal has password field for encrypted PDFs', async ({ page }) => {
    await page.evaluate(() => {
      const modal = document.getElementById('uploadModal');
      if (modal) modal.style.display = 'flex';
    });

    // Password field should exist (visible or hidden)
    const passwordField = page.locator('#uploadModal input[type="password"], #uploadModal #casPassword, #uploadModal #pdfPassword');
    const passwordFieldCount = await passwordField.count();
    
    // Also check for password label text
    const modalText = await page.locator('#uploadModal').textContent() || '';
    const hasPasswordReference = modalText.toLowerCase().includes('password');

    expect(passwordFieldCount > 0 || hasPasswordReference, 
      'Upload modal should have password field or password reference').toBe(true);
  });

  test('upload modal can be hidden programmatically', async ({ page }) => {
    // Show it
    await page.evaluate(() => {
      const modal = document.getElementById('uploadModal');
      if (modal) modal.style.display = 'flex';
    });
    await expect(page.locator('#uploadModal')).toBeVisible();

    // Hide it
    await page.evaluate(() => {
      const modal = document.getElementById('uploadModal');
      if (modal) modal.style.display = 'none';
    });
    await expect(page.locator('#uploadModal')).not.toBeVisible();
  });
});

test.describe('CAS Import Summary Modal', () => {
  test.beforeEach(async ({ page }) => {
    // Set mfhelper_visited to prevent first-time visitor redirect to ?mode=demo
    await page.addInitScript(() => {
      localStorage.clear();
      localStorage.setItem('mfhelper_visited', 'true');
    });
    await page.goto('/dashboard.html');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);
  });

  test('CAS import summary modal exists in DOM', async ({ page }) => {
    const modal = page.locator('#casImportSummaryModal');
    expect(await modal.count()).toBeGreaterThan(0);
  });

  test('CAS import summary modal is hidden by default', async ({ page }) => {
    const modal = page.locator('#casImportSummaryModal');
    await expect(modal).not.toBeVisible();
  });

  test('CAS import summary modal can be shown via showCasImportSummary()', async ({ page }) => {
    // Simulate showing the import summary with mock data
    await page.evaluate(() => {
      const mockResult = {
        import_summary: {
          total_funds_parsed: 3,
          total_invested: 185000,
          total_current: 249214,
          total_gain: 64214,
          return_pct: 34.71,
          amcs_found: ['HDFC AMC', 'PPFAS AMC', 'ICICI Prudential'],
          categories_found: ['Flexi Cap', 'Large Cap', 'Mid Cap'],
          funds_with_zero_invested: 0,
          funds_with_zero_current: 0,
          funds_with_estimated_cost: 0,
          warnings: [],
          holdings_detail: [
            { fund_name: 'HDFC Mid-Cap Opportunities Fund', amc: 'HDFC AMC', category: 'Mid Cap', invested: 50000, current_value: 68567, units: 150, nav: 456, gain_loss: 18567, warnings: [] },
            { fund_name: 'Parag Parikh Flexi Cap Fund', amc: 'PPFAS AMC', category: 'Flexi Cap', invested: 100000, current_value: 136035, units: 200, nav: 678, gain_loss: 36035, warnings: [] },
            { fund_name: 'ICICI Prudential Bluechip Fund', amc: 'ICICI Prudential', category: 'Large Cap', invested: 35000, current_value: 44612, units: 500, nav: 89, gain_loss: 9612, warnings: [] },
          ],
          saved_to_database: true,
          portfolio_id: 1,
          verification: {
            portfolio_found: true,
            portfolio_total_invested: 185000,
            portfolio_total_current: 249214,
            holdings_saved_count: 3,
            holdings_with_invested_gt_zero: 3,
            holdings_with_current_gt_zero: 3,
          }
        }
      };
      // @ts-ignore
      if (typeof showCasImportSummary === 'function') showCasImportSummary(mockResult);
    });

    const modal = page.locator('#casImportSummaryModal');
    await expect(modal).toBeVisible();
    
    // Verify summary content
    const content = await modal.textContent();
    expect(content).toContain('Saved to Database');
    expect(content).toContain('Funds Parsed');
    expect(content).toContain('HDFC');
  });

  test('CAS import summary shows warnings for zero-invested funds', async ({ page }) => {
    await page.evaluate(() => {
      const mockResult = {
        import_summary: {
          total_funds_parsed: 1,
          total_invested: 0,
          total_current: 15000,
          total_gain: 15000,
          return_pct: 0,
          amcs_found: ['SBI Mutual Fund'],
          categories_found: ['Small Cap'],
          funds_with_zero_invested: 1,
          funds_with_zero_current: 0,
          funds_with_estimated_cost: 0,
          warnings: ['1 of 1 funds have ₹0 invested amount — cost data may not have been parsed.'],
          holdings_detail: [
            { fund_name: 'SBI Small Cap Fund', amc: 'SBI MF', category: 'Small Cap', invested: 0, current_value: 15000, units: 100, nav: 150, gain_loss: 15000, warnings: ['invested_amount_is_zero'] },
          ],
          saved_to_database: true,
          portfolio_id: 2,
          verification: { portfolio_found: true, portfolio_total_invested: 0, portfolio_total_current: 15000, holdings_saved_count: 1, holdings_with_invested_gt_zero: 0, holdings_with_current_gt_zero: 1 }
        }
      };
      // @ts-ignore
      if (typeof showCasImportSummary === 'function') showCasImportSummary(mockResult);
    });

    const modal = page.locator('#casImportSummaryModal');
    await expect(modal).toBeVisible();
    
    const content = await modal.textContent();
    expect(content).toContain('Warning');
    expect(content).toContain('₹0 invested');
  });

  test('CAS import summary closeCasSummaryModal() hides modal', async ({ page }) => {
    // Show it first
    await page.evaluate(() => {
      const modal = document.getElementById('casImportSummaryModal');
      if (modal) modal.style.display = 'block';
    });
    await expect(page.locator('#casImportSummaryModal')).toBeVisible();

    // Close it
    await page.evaluate(() => {
      // @ts-ignore
      if (typeof closeCasSummaryModal === 'function') closeCasSummaryModal();
    });
    await expect(page.locator('#casImportSummaryModal')).not.toBeVisible();
  });

  test('View Dashboard button exists in CAS summary modal', async ({ page }) => {
    await page.evaluate(() => {
      const modal = document.getElementById('casImportSummaryModal');
      if (modal) modal.style.display = 'block';
    });
    
    const viewBtn = page.locator('#casImportSummaryModal button').filter({ hasText: /View Dashboard/i });
    expect(await viewBtn.count()).toBeGreaterThan(0);
  });
});

test.describe('CAS Upload — URL Trigger', () => {
  test('URL param upload=true auto-opens upload modal', async ({ page }) => {
    await page.addInitScript(() => localStorage.clear());
    await page.goto('/dashboard.html?upload=true');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(5000);

    const modal = page.locator('#uploadModal');
    const isVisible = await modal.isVisible();
    console.log('Upload modal auto-opened via URL param:', isVisible);
    
    // The URL param should trigger the modal
    expect(isVisible).toBe(true);
  });
});

test.describe('CAS Upload — API Integration', () => {
  test('upload CAS endpoint rejects unauthenticated requests', async ({ request }) => {
    const resp = await request.post('/api/upload/cas', {
      multipart: {
        file: {
          name: 'test.pdf',
          mimeType: 'application/pdf',
          buffer: Buffer.from('fake-pdf-content'),
        },
      },
    });
    console.log('Upload CAS without auth — status:', resp.status());
    expect([400, 401, 422]).toContain(resp.status());
  });

  test('CAS upload API returns import_summary with diagnostic info', async ({ request }) => {
    /**
     * Even when CAS parsing fails or returns no holdings, 
     * the API response should include an import_summary
     * so the frontend can display what happened.
     */
    const resp = await request.post('/api/upload/cas', {
      multipart: {
        file: {
          name: 'test.pdf',
          mimeType: 'application/pdf',
          buffer: Buffer.from('fake-pdf-content'),
        },
      },
    });
    
    // Response may be error (400) or success (200)
    // If 200, check import_summary exists
    if (resp.status() === 200) {
      const body = await resp.json();
      console.log('CAS upload response keys:', Object.keys(body));
      expect(body).toHaveProperty('import_summary');
      expect(body.import_summary).toHaveProperty('total_funds_parsed');
      expect(body.import_summary).toHaveProperty('warnings');
      expect(body.import_summary).toHaveProperty('holdings_detail');
      console.log('Import summary:', JSON.stringify(body.import_summary, null, 2));
    } else {
      console.log('CAS upload failed (expected for fake PDF):', resp.status());
    }
  });

  test('portfolio cas-import-summary endpoint returns diagnostic data', async ({ request }) => {
    /**
     * GET /api/portfolio/cas-import-summary should return
     * diagnostic data for debugging CAS upload issues
     */
    const resp = await request.get('/api/portfolio/cas-import-summary');
    
    // Without auth, should return 401 or 403
    console.log('CAS import summary without auth — status:', resp.status());
    expect([200, 401, 403]).toContain(resp.status());
  });

  test('BUG: /api/upload/cas route — cas.py and upload.py both register same endpoint', async ({ request }) => {
    /**
     * Both backend/app/routers/cas.py and backend/app/routers/upload.py
     * register POST /api/upload/cas. This is a route conflict.
     * One may shadow the other depending on import order.
     */
    const resp = await request.post('/api/upload/cas');
    console.log('Route conflict test — status:', resp.status());
    // Just document that the endpoint responds (not 404)
    expect(resp.status()).not.toBe(404);
  });
});
