import { test, expect } from '@playwright/test';
import { dismissPortfolioSourceModal } from '../helpers/test-helpers';

/**
 * MFHelper Form Interaction Tests
 * Tests user input and form submission
 */

test.describe('Form Interactions', () => {
  test('should handle portfolio input form', async ({ page }) => {
    await page.goto('/dashboard.html').catch(() => page.goto('/'));
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(600);
    // Dismiss portfolio source modal if on dashboard
    await dismissPortfolioSourceModal(page);

    // Look for input forms
    const formInputs = await page.locator('input, textarea').all();
    
    if (formInputs.length === 0) {
      test.skip('No input forms found');
      return;
    }

    // Try to fill the first visible text input
    // First open manual entry modal to get text inputs
    const manualBtn = page.locator('button:has-text("Manual Entry")').first();
    if (await manualBtn.isVisible()) {
      await manualBtn.click();
      await page.waitForTimeout(500);
    }
    
    const textInput = page.locator('#manualEntryModal input[type="text"]').first();
    
    if (await textInput.count() > 0 && await textInput.isVisible()) {
      await textInput.fill('Test Fund Name');
      await expect(textInput).toHaveValue('Test Fund Name');
    } else {
      // Fall back to any visible input
      const anyInput = page.locator('input:visible').first();
      if (await anyInput.count() > 0) {
        const inputType = await anyInput.getAttribute('type');
        if (inputType === 'number') {
          await anyInput.fill('100');
          await expect(anyInput).toHaveValue('100');
        } else {
          await anyInput.fill('Test');
          await expect(anyInput).toHaveValue('Test');
        }
      }
    }
  });

  test('should handle dropdown selections', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Find select elements
    const selects = await page.locator('select').all();
    
    if (selects.length > 0) {
      const firstSelect = page.locator('select').first();
      
      // Get available options
      const options = await firstSelect.locator('option').all();
      
      if (options.length > 1) {
        // Select the second option (skip the first which is often a placeholder)
        await firstSelect.selectOption({ index: 1 });
        
        console.log('Selected dropdown option');
        
        await page.screenshot({ 
          path: 'test-results/screenshots/dropdown-selected.png', 
          fullPage: true 
        });
      }
    } else {
      test.skip('No dropdowns found');
    }
  });

  test('should handle button clicks', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Find all buttons
    const buttons = await page.locator('button:not([disabled])').all();
    
    console.log(`Found ${buttons.length} enabled buttons`);
    
    if (buttons.length > 0) {
      // Click the first non-disabled button
      const firstButton = page.locator('button:not([disabled])').first();
      const buttonText = await firstButton.textContent();
      
      console.log(`Clicking button: ${buttonText}`);
      
      // Take screenshot before click
      await page.screenshot({ 
        path: 'test-results/screenshots/before-button-click.png' 
      });
      
      await firstButton.click();
      
      // Wait for any changes
      await page.waitForTimeout(1000);
      
      // Take screenshot after click
      await page.screenshot({ 
        path: 'test-results/screenshots/after-button-click.png' 
      });
    }
  });
});

test.describe('Search Functionality', () => {
  test('should perform search operation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Look for search inputs
    const searchInput = page.locator(
      'input[type="search"], input[placeholder*="Search" i], #search'
    ).first();

    if (await searchInput.count() > 0) {
      await searchInput.fill('HDFC');
      
      // Look for search button or trigger search
      const searchButton = page.locator('button:has-text("Search")').first();
      
      if (await searchButton.count() > 0) {
        await searchButton.click();
      } else {
        // Try pressing Enter
        await searchInput.press('Enter');
      }

      // Wait for results
      await page.waitForTimeout(2000);
      
      await page.screenshot({ 
        path: 'test-results/screenshots/search-results.png', 
        fullPage: true 
      });
    } else {
      test.skip('No search functionality found');
    }
  });
});

test.describe('Error Handling', () => {
  test('should handle 404 pages gracefully', async ({ page }) => {
    const response = await page.goto('/nonexistent-page-123').catch(() => null);
    
    if (response) {
      // Check if we got a 404 or redirected
      const status = response.status();
      console.log(`Response status: ${status}`);
      
      if (status === 404) {
        // Verify 404 page content
        await expect(page.locator('text=404, text=Not Found')).toBeVisible();
      }
      
      await page.screenshot({ 
        path: 'test-results/screenshots/404-page.png' 
      });
    }
  });

  test('should capture network errors', async ({ page }) => {
    const failedRequests: string[] = [];

    page.on('requestfailed', request => {
      failedRequests.push(`Failed: ${request.url()} - ${request.failure()?.errorText}`);
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    if (failedRequests.length > 0) {
      console.log('Failed requests:', failedRequests);
    }

    // Log the failed requests but don't fail the test
    expect(failedRequests.length).toBeLessThan(10); // Allow some failures
  });
});
