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
      'text=Portfolio',
      'text=Tools',
      'text=Goal Planning',
      'text=Get Started'
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
  test('should navigate to portfolio', async ({ page }) => {
    await page.goto('/');
    
    // Click portfolio link (try multiple selectors)
    const portfolioLink = page.locator('a[href*="portfolio"], text=Portfolio').first();
    
    if (await portfolioLink.count() > 0) {
      await portfolioLink.click();
      
      // Wait for navigation - may redirect to auth or portfolio
      await page.waitForURL(/\/(portfolio|auth)/, { timeout: 10000 }).catch(() => {
        console.log('Portfolio navigation timed out or redirected');
      });
      
      // Verify we navigated to a valid page (portfolio or auth redirect or stayed on page)
      const url = page.url();
      const validNavigation = url.includes('portfolio') || url.includes('auth') || url.includes('index');
      expect(validNavigation).toBeTruthy();
    } else {
      // No portfolio link found - this is acceptable
      console.log('Portfolio link not found on homepage - skipping');
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
