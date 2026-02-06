import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('File Upload', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8000/dashboard.html');
    await page.waitForLoadState('networkidle');
  });

  test('should open upload modal', async ({ page }) => {
    await page.click('text=Upload Portfolio');
    await expect(page.locator('#uploadModal')).toBeVisible();
    console.log('✅ Upload modal opens');
  });

  test('should show PDF password field for PDF files', async ({ page }) => {
    await page.click('text=Upload Portfolio');
    await expect(page.locator('#uploadModal')).toBeVisible();
    
    // The password section should be hidden initially
    const passwordSection = page.locator('#pdfPasswordSection');
    await expect(passwordSection).toBeHidden();
    
    // Simulate file selection (we'll check if password field appears)
    await page.evaluate(() => {
      const event = new Event('change');
      const input = document.getElementById('fileInput') as HTMLInputElement;
      if (input) {
        // Simulate PDF file selection
        Object.defineProperty(input, 'files', {
          value: [{
            name: 'test.pdf',
            type: 'application/pdf',
            size: 1024
          }]
        });
        input.dispatchEvent(event);
      }
    });
    
    await page.waitForTimeout(500);
    // Password field should now be visible for PDF
    await expect(passwordSection).toBeVisible();
    
    console.log('✅ Password field shows for PDF files');
  });

  test('should enable upload button after file selection', async ({ page }) => {
    await page.click('text=Upload Portfolio');
    await expect(page.locator('#uploadModal')).toBeVisible();
    
    const uploadBtn = page.locator('#uploadButton');
    await expect(uploadBtn).toBeDisabled();
    
    // Simulate file selection
    await page.evaluate(() => {
      const event = new Event('change');
      const input = document.getElementById('fileInput') as HTMLInputElement;
      if (input) {
        Object.defineProperty(input, 'files', {
          value: [{
            name: 'test.xlsx',
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            size: 2048
          }]
        });
        input.dispatchEvent(event);
      }
    });
    
    await page.waitForTimeout(500);
    await expect(uploadBtn).not.toBeDisabled();
    
    console.log('✅ Upload button enabled after file selection');
  });

  test('should close modal on Cancel', async ({ page }) => {
    await page.click('text=Upload Portfolio');
    await expect(page.locator('#uploadModal')).toBeVisible();
    
    await page.click('#uploadModal button:has-text("Cancel")');
    await expect(page.locator('#uploadModal')).not.toBeVisible();
    
    console.log('✅ Upload modal closes on Cancel');
  });

  test('should check for JavaScript errors during upload flow', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    await page.click('text=Upload Portfolio');
    await expect(page.locator('#uploadModal')).toBeVisible();
    await page.waitForTimeout(1000);
    
    expect(errors).toHaveLength(0);
    console.log('✅ No JavaScript errors in upload flow');
  });
});
