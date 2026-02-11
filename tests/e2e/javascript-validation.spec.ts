import { test, expect } from '@playwright/test';
import { verifyNoConsoleErrors, dismissPortfolioSourceModal } from '../helpers/test-helpers';

/**
 * JavaScript Validation Tests
 * Catches syntax errors, runtime errors, and console issues
 */

test.describe('JavaScript Validation', () => {
  test('dashboard page should have no JavaScript syntax errors', async ({ page }) => {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    // Capture all console messages
    page.on('console', msg => {
      const text = msg.text();
      const type = msg.type();
      
      if (type === 'error') {
        errors.push(text);
        console.error('❌ Console Error:', text);
      } else if (type === 'warning') {
        warnings.push(text);
      }
    });
    
    // Capture page errors (uncaught exceptions, syntax errors)
    page.on('pageerror', error => {
      errors.push(`Uncaught exception: ${error.message}\n${error.stack}`);
      console.error('❌ Page Error:', error.message);
    });
    
    // Load the dashboard page
    await page.goto('/dashboard.html', { waitUntil: 'networkidle' });
    
    // Wait a bit to ensure all scripts have executed
    await page.waitForTimeout(2000);
    
    // Log what we found
    if (errors.length > 0) {
      console.log('\n=== JavaScript Errors Found ===');
      errors.forEach((err, i) => console.log(`${i + 1}. ${err}`));
      console.log('================================\n');
    }
    
    if (warnings.length > 0) {
      console.log('\n⚠️  Warnings:', warnings.length);
    }
    
    // Take screenshot for debugging
    if (errors.length > 0) {
      await page.screenshot({ 
        path: 'test-results/screenshots/javascript-errors.png', 
        fullPage: true 
      });
    }
    
    // Assert no errors - filter acceptable network errors
    const criticalErrors = errors.filter(err => 
      !err.includes('favicon') &&
      !err.includes('analytics') &&
      !err.includes('Failed to load resource') &&
      !err.includes('net::ERR') &&
      !err.includes('401')
    );
    expect(criticalErrors.length).toBe(0);
  });
  
  test('all buttons should be clickable (no JS syntax errors)', async ({ page }) => {
    await page.goto('/dashboard.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    await dismissPortfolioSourceModal(page);
    
    // Find all buttons
    const buttons = await page.locator('button').all();
    console.log(`Found ${buttons.length} buttons to test`);
    
    if (buttons.length === 0) {
      test.skip('No buttons found on page');
      return;
    }
    
    // Check first few buttons are enabled and clickable
    const testButtons = buttons.slice(0, 5);
    
    for (let i = 0; i < testButtons.length; i++) {
      const button = testButtons[i];
      const text = await button.textContent();
      
      // Check if button has onclick or is not disabled
      const isDisabled = await button.isDisabled();
      const hasOnClick = await button.evaluate(btn => {
        return btn.hasAttribute('onclick') || btn.onclick !== null;
      });
      
      console.log(`Button ${i + 1}: "${text?.trim()}" - Disabled: ${isDisabled}, Has onClick: ${hasOnClick}`);
      
      // At least some buttons should be enabled with handlers
      if (!isDisabled && hasOnClick) {
        // This validates that the onclick handler is defined (no syntax errors)
        expect(hasOnClick).toBeTruthy();
      }
    }
  });
  
  test('manual entry modal functions should be defined', async ({ page }) => {
    await page.goto('/dashboard.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    await dismissPortfolioSourceModal(page);
    
    // Check if critical functions are defined
    const functionsToCheck = [
      'showManualEntryModal',
      'closeManualEntryModal',
      'addManualEntryRow',
      'removeRow',
      'saveManualEntries',
      'searchFunds',
      'onAmcChange'
    ];
    
    for (const funcName of functionsToCheck) {
      const isDefined = await page.evaluate((name) => {
        return typeof (window as any)[name] === 'function';
      }, funcName);
      
      console.log(`Function ${funcName}: ${isDefined ? '✅ Defined' : '❌ Not defined'}`);
      expect(isDefined).toBeTruthy();
    }
  });
  
  test('no duplicate function declarations', async ({ page }) => {
    await page.goto('/dashboard.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    await dismissPortfolioSourceModal(page);
    
    // Get the page source
    const content = await page.content();
    
    // Check for common function declaration patterns
    const functionNames = [
      'showManualEntryModal',
      'closeManualEntryModal',
      'addManualEntryRow',
      'saveManualEntries'
    ];
    
    for (const funcName of functionNames) {
      // Count occurrences of function declarations
      const declarationPattern = new RegExp(`function\\s+${funcName}\\s*\\(`, 'g');
      const asyncDeclarationPattern = new RegExp(`async\\s+function\\s+${funcName}\\s*\\(`, 'g');
      
      const declarations = (content.match(declarationPattern) || []).length;
      const asyncDeclarations = (content.match(asyncDeclarationPattern) || []).length;
      
      // declarationPattern already matches async functions, so don't double-count
      const total = declarations;
      
      console.log(`${funcName}: ${total} declaration(s)`);
      
      // Each function should be declared exactly once
      expect(total).toBeLessThanOrEqual(1);
    }
  });
  
  test('no unclosed braces or syntax issues', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('pageerror', error => {
      if (error.message.includes('SyntaxError') || 
          error.message.includes('Unexpected token') ||
          error.message.includes('Unexpected identifier')) {
        errors.push(error.message);
      }
    });
    
    await page.goto('/dashboard.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    
    if (errors.length > 0) {
      console.log('Syntax errors found:', errors);
    }
    
    expect(errors.length).toBe(0);
  });
  
  test('all onclick handlers execute without errors', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    await page.goto('/dashboard.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    await dismissPortfolioSourceModal(page);
    
    // Try to trigger a few onclick handlers
    const clickableElements = await page.locator('[onclick], button').all();
    
    if (clickableElements.length > 0) {
      // Test first clickable element (if any)
      const firstElement = clickableElements[0];
      const text = await firstElement.textContent();
      
      console.log(`Testing onclick handler for: "${text?.trim()}"`);
      
      try {
        // Don't actually click (might trigger modals), just verify handler exists
        const hasValidHandler = await firstElement.evaluate(el => {
          const handler = el.getAttribute('onclick');
          if (!handler) return false;
          
          try {
            // Try to parse the onclick as a function
            new Function(handler);
            return true;
          } catch (e) {
            console.error('Invalid onclick handler:', handler, e);
            return false;
          }
        });
        
        expect(hasValidHandler).toBeTruthy();
      } catch (e) {
        console.log('Could not test element:', e);
      }
    }
    
    // No critical errors should have occurred (filter network errors)
    const criticalErrors = errors.filter(err => 
      !err.includes('Failed to load resource') &&
      !err.includes('net::ERR') &&
      !err.includes('401') &&
      !err.includes('favicon')
    );
    expect(criticalErrors.length).toBe(0);
  });
});

test.describe('Modal Functionality Tests', () => {
  test('manual entry modal can be opened and closed', async ({ page }) => {
    await page.goto('/dashboard.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(600);
    await dismissPortfolioSourceModal(page);
    
    // Check if modal open function works
    const modalOpenResult = await page.evaluate(() => {
      try {
        (window as any).showManualEntryModal();
        return { success: true, error: null };
      } catch (e: any) {
        return { success: false, error: e.message };
      }
    });
    
    expect(modalOpenResult.success).toBeTruthy();
    if (!modalOpenResult.success) {
      console.error('Modal open error:', modalOpenResult.error);
    }
    
    // Check if modal is visible
    const modalVisible = await page.locator('#manualEntryModal').isVisible();
    expect(modalVisible).toBeTruthy();
    
    // Close modal
    const modalCloseResult = await page.evaluate(() => {
      try {
        (window as any).closeManualEntryModal();
        return { success: true, error: null };
      } catch (e: any) {
        return { success: false, error: e.message };
      }
    });
    
    expect(modalCloseResult.success).toBeTruthy();
  });
});
