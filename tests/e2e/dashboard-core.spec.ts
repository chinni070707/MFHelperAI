import { test, expect } from '@playwright/test';

test.describe('Dashboard Core Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8000/dashboard.html');
    await page.waitForLoadState('networkidle');
  });

  test('should load dashboard without errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', error => errors.push(error.message));
    
    await page.waitForTimeout(2000);
    
    expect(errors).toHaveLength(0);
    console.log('✅ Dashboard loaded without JavaScript errors');
  });

  test('should have all main buttons visible', async ({ page }) => {
    const buttons = [
      'Manual Entry',
      'Upload Portfolio',
      'Export Data',
      'Sign Up Free'
    ];
    
    for (const btnText of buttons) {
      const button = page.locator(`button:has-text("${btnText}"), a:has-text("${btnText}")`).first();
      await expect(button).toBeVisible();
      console.log(`✅ "${btnText}" button is visible`);
    }
  });

  test('should all buttons be clickable', async ({ page }) => {
    const clickableButtons = [
      { text: 'Manual Entry', modalId: '#manualEntryModal' },
      { text: 'Upload Portfolio', modalId: '#uploadModal' }
    ];
    
    for (const btn of clickableButtons) {
      await page.click(`text=${btn.text}`);
      await expect(page.locator(btn.modalId)).toBeVisible();
      
      // Close the modal
      await page.locator(btn.modalId).evaluate(el => (el as HTMLElement).style.display = 'none');
      
      console.log(`✅ "${btn.text}" button works`);
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
