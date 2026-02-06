/**
 * Test Helper Utilities for MFHelper Web Application
 * Following webapp-testing skill patterns
 */

import { Page, expect } from '@playwright/test';

/**
 * Wait for a condition to be true with timeout
 * Pattern from webapp-testing skill
 */
export async function waitForCondition(
  condition: () => Promise<boolean>,
  timeout = 5000,
  interval = 100
): Promise<boolean> {
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return true;
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  throw new Error('Condition not met within timeout');
}

/**
 * Capture browser console logs
 * Pattern from webapp-testing skill
 */
export function captureConsoleLogs(page: Page): Array<{ type: string; text: string; timestamp: string }> {
  const logs: Array<{ type: string; text: string; timestamp: string }> = [];
  
  page.on('console', msg => {
    logs.push({
      type: msg.type(),
      text: msg.text(),
      timestamp: new Date().toISOString()
    });
  });
  
  return logs;
}

/**
 * Take screenshot with automatic naming
 * Pattern from webapp-testing skill
 */
export async function captureScreenshot(page: Page, name: string): Promise<string> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `test-results/screenshots/${name}-${timestamp}.png`;
  
  await page.screenshot({ path: filename, fullPage: true });
  console.log(`Screenshot saved: ${filename}`);
  
  return filename;
}

/**
 * Wait for element to be visible with retry
 */
export async function waitForElement(
  page: Page,
  selector: string,
  timeout = 5000
): Promise<boolean> {
  try {
    await page.waitForSelector(selector, { state: 'visible', timeout });
    return true;
  } catch (error) {
    console.log(`Element ${selector} not found within ${timeout}ms`);
    return false;
  }
}

/**
 * Check if element exists without throwing error
 */
export async function elementExists(page: Page, selector: string): Promise<boolean> {
  return (await page.locator(selector).count()) > 0;
}

/**
 * Fill form with data object
 */
export async function fillForm(page: Page, formData: Record<string, string>): Promise<void> {
  for (const [selector, value] of Object.entries(formData)) {
    const element = page.locator(selector);
    
    if (await element.count() > 0) {
      const tagName = await element.evaluate(el => el.tagName.toLowerCase());
      
      if (tagName === 'select') {
        await element.selectOption(value);
      } else {
        await element.fill(value);
      }
    }
  }
}

/**
 * Wait for navigation with timeout
 */
export async function waitForNavigation(
  page: Page,
  urlPattern: string,
  timeout = 10000
): Promise<boolean> {
  try {
    await page.waitForURL(urlPattern, { timeout });
    return true;
  } catch (error) {
    console.log(`Navigation to ${urlPattern} timed out`);
    return false;
  }
}

/**
 * Capture network errors during page load
 */
export function captureNetworkErrors(page: Page): string[] {
  const errors: string[] = [];
  
  page.on('requestfailed', request => {
    errors.push(`${request.url()} - ${request.failure()?.errorText}`);
  });
  
  return errors;
}

/**
 * Get text content of all matching elements
 */
export async function getTexts(page: Page, selector: string): Promise<string[]> {
  const elements = await page.locator(selector).all();
  const texts: string[] = [];
  
  for (const element of elements) {
    const text = await element.textContent();
    if (text) {
      texts.push(text.trim());
    }
  }
  
  return texts;
}

/**
 * Click element with retry and error handling
 */
export async function clickWithRetry(
  page: Page,
  selector: string,
  maxRetries = 3
): Promise<boolean> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await page.locator(selector).first().click({ timeout: 5000 });
      return true;
    } catch (error) {
      console.log(`Click attempt ${i + 1} failed for ${selector}`);
      if (i < maxRetries - 1) {
        await page.waitForTimeout(1000);
      }
    }
  }
  return false;
}

/**
 * Verify page has no console errors
 */
export async function verifyNoConsoleErrors(page: Page, timeout = 3000): Promise<void> {
  const errors: string[] = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  page.on('pageerror', error => {
    errors.push(error.message);
  });
  
  await page.waitForTimeout(timeout);
  
  if (errors.length > 0) {
    console.log('Console errors detected:', errors);
  }
  
  expect(errors.length).toBe(0);
}

/**
 * Take screenshot on test failure
 */
export async function screenshotOnFailure(page: Page, testInfo: any): Promise<void> {
  if (testInfo.status !== testInfo.expectedStatus) {
    const screenshotPath = testInfo.outputPath(`failure-${testInfo.title}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`Failure screenshot saved: ${screenshotPath}`);
  }
}
