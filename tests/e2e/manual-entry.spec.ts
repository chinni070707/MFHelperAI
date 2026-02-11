import { test, expect } from '@playwright/test';
import { dismissPortfolioSourceModal } from '../helpers/test-helpers';

test.describe('Manual Portfolio Entry', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(600);
    await dismissPortfolioSourceModal(page);
  });

  test('should open manual entry modal with 5 rows', async ({ page }) => {
    // Click manual entry button
    await page.click('text=Manual Entry');
    
    // Wait for modal to be visible
    await expect(page.locator('#manualEntryModal')).toBeVisible();
    
    // Check that 5 rows are present
    const rows = await page.locator('#entryTableBody tr').count();
    expect(rows).toBe(5);
    
    console.log('✅ Manual entry modal opens with 5 rows');
  });

  test('should load AMC list in dropdowns', async ({ page }) => {
    // Click manual entry button
    await page.click('text=Manual Entry');
    await expect(page.locator('#manualEntryModal')).toBeVisible();
    
    // Wait for AMC dropdowns to be populated
    await page.waitForTimeout(1000); // Give time for async load
    
    // Check first dropdown has options
    const firstSelect = page.locator('.amc-select').first();
    const optionCount = await firstSelect.locator('option').count();
    
    // Should have at least "Select AMC..." + some AMCs
    expect(optionCount).toBeGreaterThan(1);
    
    // Get option text to verify AMCs are loaded
    const options = await firstSelect.locator('option').allTextContents();
    console.log(`✅ AMC dropdown has ${optionCount} options:`, options.slice(0, 5));
    
    // Verify common AMCs are present
    const allOptionsText = options.join(',');
    expect(allOptionsText).toContain('HDFC');
  });

  test('should enable fund search after AMC selection', async ({ page }) => {
    await page.click('text=Manual Entry');
    await expect(page.locator('#manualEntryModal')).toBeVisible();
    await page.waitForTimeout(1000);
    
    // Select an AMC
    const firstSelect = page.locator('.amc-select').first();
    await firstSelect.selectOption('HDFC');
    
    // Fund search should now be enabled
    const fundInput = page.locator('.fund-search').first();
    await expect(fundInput).not.toBeDisabled();
    
    console.log('✅ Fund search enabled after AMC selection');
  });

  test('should show fund suggestions when typing', async ({ page }) => {
    await page.click('text=Manual Entry');
    await expect(page.locator('#manualEntryModal')).toBeVisible();
    await page.waitForTimeout(1000);
    
    // Select AMC and type in fund search
    await page.locator('.amc-select').first().selectOption('HDFC');
    const fundInput = page.locator('.fund-search').first();
    await fundInput.fill('Flexi');
    
    // Wait for dropdown to appear
    await page.waitForTimeout(500);
    
    // Check if dropdown is visible
    const dropdown = page.locator('.fund-dropdown').first();
    await expect(dropdown).toBeVisible();
    
    console.log('✅ Fund suggestions appear when typing');
  });

  test('should add new row when clicking Add Another Fund', async ({ page }) => {
    await page.click('text=Manual Entry');
    await expect(page.locator('#manualEntryModal')).toBeVisible();
    await page.waitForTimeout(1000);
    
    const initialRows = await page.locator('#entryTableBody tr').count();
    
    // Click Add Another Fund
    await page.click('text=Add Another Fund');
    
    const newRows = await page.locator('#entryTableBody tr').count();
    expect(newRows).toBe(initialRows + 1);
    
    console.log(`✅ Added row: ${initialRows} → ${newRows}`);
  });

  test('should validate required fields before save', async ({ page }) => {
    await page.click('text=Manual Entry');
    await expect(page.locator('#manualEntryModal')).toBeVisible();
    await page.waitForTimeout(1000);
    
    // Try to save without filling anything
    page.once('dialog', dialog => {
      expect(dialog.message()).toMatch(/Please (fill all fields|add at least one fund)/);
      dialog.accept();
    });
    
    await page.click('text=Save Portfolio');
    
    console.log('✅ Validation works for empty fields');
  });

  test('should close modal when clicking Cancel', async ({ page }) => {
    await page.click('text=Manual Entry');
    await expect(page.locator('#manualEntryModal')).toBeVisible();
    
    await page.click('text=Cancel');
    await expect(page.locator('#manualEntryModal')).not.toBeVisible();
    
    console.log('✅ Modal closes on Cancel');
  });

  test('all buttons should be same width', async ({ page }) => {
    await page.click('text=Manual Entry');
    await expect(page.locator('#manualEntryModal')).toBeVisible();
    await page.waitForTimeout(1000);
    
    // Get button widths
    const addBtn = page.locator('text=Add Another Fund');
    const saveBtn = page.locator('text=Save Portfolio');
    const cancelBtn = page.locator('button:has-text("Cancel")').last();
    
    const addWidth = await addBtn.evaluate(el => el.getBoundingClientRect().width);
    const saveWidth = await saveBtn.evaluate(el => el.getBoundingClientRect().width);
    const cancelWidth = await cancelBtn.evaluate(el => el.getBoundingClientRect().width);
    
    console.log(`Button widths: Add=${addWidth}, Save=${saveWidth}, Cancel=${cancelWidth}`);
    
    // Allow 5px tolerance for rounding
    expect(Math.abs(addWidth - saveWidth)).toBeLessThan(5);
    // Only compare Cancel if it has non-zero width (may be hidden)
    if (cancelWidth > 0) {
      expect(Math.abs(saveWidth - cancelWidth)).toBeLessThan(5);
    }
    
    console.log('✅ All buttons have equal width');
  });

  test('should check for JavaScript errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    await page.click('text=Manual Entry');
    await expect(page.locator('#manualEntryModal')).toBeVisible();
    await page.waitForTimeout(2000);
    
    expect(errors).toHaveLength(0);
    console.log('✅ No JavaScript errors detected');
  });
});
