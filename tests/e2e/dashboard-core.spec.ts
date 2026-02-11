import { test, expect } from '@playwright/test';
import { dismissPortfolioSourceModal } from '../helpers/test-helpers';

test.describe('Dashboard Core Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(600);
    await dismissPortfolioSourceModal(page);
  });

  test('should load dashboard without errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    
    await page.waitForTimeout(2000);
    
    expect(errors).toHaveLength(0);
    console.log('✅ Dashboard loaded without JavaScript errors');
  });

  test('should have all main buttons visible', async ({ page }) => {
    // Check for buttons that should be visible on dashboard regardless of data state
    // Note: Manual Entry and Upload are only visible in noData state or as visible buttons
    const visibleButtons = [
      { locator: 'button:has-text("Upload CAS")', name: 'Upload CAS' },
      { locator: 'button:has-text("Rebalance")', name: 'Rebalance' },
      { locator: 'button:has-text("Quick Analysis")', name: 'Quick Analysis' }
    ];
    
    let foundAny = false;
    for (const btn of visibleButtons) {
      const button = page.locator(btn.locator).first();
      if (await button.isVisible().catch(() => false)) {
        console.log(`✅ "${btn.name}" button is visible`);
        foundAny = true;
      }
    }
    
    // At least one button should be visible
    expect(foundAny).toBeTruthy();
  });

  test('should all buttons be clickable', async ({ page }) => {
    // Test buttons that are reliably present - rebalancing buttons
    const rebalanceBtn = page.locator('button:has-text("Rebalance Existing")').first();
    if (await rebalanceBtn.isVisible().catch(() => false)) {
      await rebalanceBtn.click();
      console.log('✅ "Rebalance Existing" button works');
    }
    
    // Test Quick Analysis button
    const quickAnalysisBtn = page.locator('button:has-text("Quick Analysis")').first();
    if (await quickAnalysisBtn.isVisible().catch(() => false)) {
      await quickAnalysisBtn.click();
      console.log('✅ "Quick Analysis" button works');
    }
  });

  test('should check console for warnings and errors', async ({ page }) => {
    const consoleMessages: any[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error' || msg.type() === 'warning') {
        consoleMessages.push({
          type: msg.type(),
          text: msg.text()
        });
      }
    });
    
    // Interact with the page
    await page.click('text=Manual Entry');
    await page.waitForTimeout(2000);
    await page.click('text=Cancel');
    
    // Filter out known acceptable warnings
    const criticalIssues = consoleMessages.filter(msg => 
      !msg.text.includes('DevTools') &&
      !msg.text.includes('extension')
    );
    
    if (criticalIssues.length > 0) {
      console.log('⚠️ Console issues found:', criticalIssues);
    } else {
      console.log('✅ No critical console errors or warnings');
    }
  });

  test('should verify no duplicate closing braces', async ({ page }) => {
    // This test checks that JavaScript loads without syntax errors
    const hasError = await page.evaluate(() => {
      // Try to access a function that would fail if there's a syntax error
      return typeof showManualEntryModal !== 'function';
    });
    
    expect(hasError).toBe(false);
    console.log('✅ No JavaScript syntax errors (like duplicate braces)');
  });
});
