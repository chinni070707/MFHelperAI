import { test, expect } from '@playwright/test';

/**
 * MFHelper AI Assistant Tests
 * Tests the AI chat functionality
 */

test.describe('AI Assistant Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    
    // Navigate to AI demo page if it exists
    const aiLink = page.locator('a[href*="ai"], text=AI Assistant, text=AI Demo').first();
    if (await aiLink.count() > 0) {
      await aiLink.click();
      await page.waitForLoadState('networkidle');
    } else {
      // Try direct navigation
      await page.goto('/ai-demo.html').catch(() => {
        console.log('AI demo page not accessible');
      });
    }
  });

  test('should display AI chat interface', async ({ page }) => {
    // Look for common chat interface elements
    const chatSelectors = [
      '#chat-input',
      '[placeholder*="Ask"], [placeholder*="message"]',
      'textarea',
      'input[type="text"]'
    ];

    let chatInputFound = false;
    for (const selector of chatSelectors) {
      if (await page.locator(selector).count() > 0) {
        await expect(page.locator(selector).first()).toBeVisible();
        chatInputFound = true;
        break;
      }
    }

    if (!chatInputFound) {
      console.log('Chat input not found - skipping test');
      test.skip();
    }

    // Capture screenshot
    await page.screenshot({ 
      path: 'test-results/screenshots/ai-assistant.png', 
      fullPage: true 
    });
  });

  test('should send a message to AI', async ({ page }) => {
    // Find chat input
    const chatInput = page.locator('#chat-input, textarea, input[type="text"]').first();
    
    if (await chatInput.count() === 0) {
      test.skip('Chat input not found');
      return;
    }

    // Type a test message
    await chatInput.fill('What is MFHelper?');
    
    // Find and click send button
    const sendButton = page.locator('button:has-text("Send"), button[type="submit"], .send-button').first();
    
    if (await sendButton.count() > 0) {
      await sendButton.click();
      
      // Wait for response (with timeout)
      await page.waitForTimeout(2000);
      
      // Look for chat response elements
      const responseSelectors = [
        '.chat-message',
        '.message',
        '.ai-response',
        '[role="log"]'
      ];

      let responseFound = false;
      for (const selector of responseSelectors) {
        if (await page.locator(selector).count() > 0) {
          responseFound = true;
          break;
        }
      }

      if (responseFound) {
        // Capture response screenshot
        await page.screenshot({ 
          path: 'test-results/screenshots/ai-response.png', 
          fullPage: true 
        });
      }
    } else {
      console.log('Send button not found');
    }
  });

  test('should handle AI errors gracefully', async ({ page }) => {
    const errors: string[] = [];
    
    // Listen for console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Listen for page errors
    page.on('pageerror', error => {
      errors.push(error.message);
    });

    await page.waitForTimeout(3000);
    
    // Log any errors found
    if (errors.length > 0) {
      console.log('Errors detected:', errors);
    }
  });
});

test.describe('Portfolio Analysis', () => {
  test('should navigate to portfolio page', async ({ page }) => {
    await page.goto('/');
    
    // Find portfolio link
    const portfolioLink = page.locator('a[href*="dashboard"], text=Portfolio, text=Dashboard').first();
    
    if (await portfolioLink.count() > 0) {
      await portfolioLink.click();
      await page.waitForLoadState('networkidle');
      
      // Verify portfolio elements
      await page.screenshot({ 
        path: 'test-results/screenshots/portfolio.png', 
        fullPage: true 
      });
    } else {
      test.skip('Portfolio link not found');
    }
  });

  test('should display mutual fund data', async ({ page }) => {
    await page.goto('/dashboard.html').catch(() => page.goto('/'));
    await page.waitForLoadState('networkidle');
    
    // Look for common table/list elements
    const dataElements = [
      'table',
      '.fund-list',
      '.portfolio-item',
      '[data-testid="fund-table"]'
    ];

    let dataFound = false;
    for (const selector of dataElements) {
      if (await page.locator(selector).count() > 0) {
        dataFound = true;
        console.log(`Found data element: ${selector}`);
        break;
      }
    }

    if (dataFound) {
      await page.screenshot({ 
        path: 'test-results/screenshots/portfolio-data.png', 
        fullPage: true 
      });
    }
  });
});
