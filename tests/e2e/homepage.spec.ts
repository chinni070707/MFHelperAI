import { test, expect, Page } from '@playwright/test';

/**
 * MFHelper Homepage Tests
 * Following webapp-testing skill patterns
 */

test.describe('Homepage Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to homepage before each test
    await page.goto('/');
  });

  test('should load homepage successfully', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/MFHelper/i);
    
    // Capture screenshot for documentation
    await page.screenshot({ 
      path: 'test-results/screenshots/homepage.png', 
      fullPage: true 
    });
  });

  test('should display main navigation elements', async ({ page }) => {
    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    // Verify key navigation elements exist
    const navElements = [
      'text=Dashboard',
      'text=Portfolio',
      'text=Analysis',
      'text=AI Assistant'
    ];

    for (const selector of navElements) {
      const element = page.locator(selector).first();
      await expect(element).toBeVisible({ timeout: 5000 });
    }
  });

  test('should handle responsive design', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500); // Allow layout to adjust
    
    // Verify mobile menu button exists
    const mobileMenu = page.locator('[aria-label="Menu"], .mobile-menu, #menu-button');
    const menuExists = await mobileMenu.count() > 0;
    
    if (menuExists) {
      await expect(mobileMenu.first()).toBeVisible();
    }
    
    // Capture mobile screenshot
    await page.screenshot({ 
      path: 'test-results/screenshots/homepage-mobile.png', 
      fullPage: true 
    });
  });

  test('should log browser console messages', async ({ page }) => {
    const consoleLogs: string[] = [];
    
    // Capture console logs
    page.on('console', msg => {
      consoleLogs.push(`[${msg.type()}] ${msg.text()}`);
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Log captured messages
    console.log('Browser Console Logs:', consoleLogs);
    
    // Check for critical errors
    const errors = consoleLogs.filter(log => log.includes('[error]'));
    expect(errors.length).toBe(0);
  });
});

test.describe('Homepage Links', () => {
  test('should navigate to dashboard', async ({ page }) => {
    await page.goto('/');
    
    // Click dashboard link (try multiple selectors)
    const dashboardLink = page.locator('a[href*="dashboard"], text=Dashboard').first();
    
    if (await dashboardLink.count() > 0) {
      await dashboardLink.click();
      
      // Wait for navigation
      await page.waitForURL('**/dashboard**', { timeout: 10000 }).catch(() => {
        console.log('Dashboard navigation timed out or redirected');
      });
      
      // Verify we're on dashboard page
      const url = page.url();
      expect(url).toContain('dashboard');
    } else {
      test.skip('Dashboard link not found on homepage');
    }
  });
});

// Helper function to wait for element with retry
async function waitForElement(page: Page, selector: string, timeout = 5000) {
  try {
    await page.waitForSelector(selector, { state: 'visible', timeout });
    return true;
  } catch (error) {
    console.log(`Element ${selector} not found within ${timeout}ms`);
    return false;
  }
}
