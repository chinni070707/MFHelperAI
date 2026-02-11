/**
 * MFHelper E2E Tests — Full User Journey
 * 
 * Tests the end-to-end flow:
 * 1. Landing page
 * 2. Auth sign-up / sign-in
 * 3. Dashboard structure verification
 * 4. Objective assessment (style + market cap analysis capabilities)
 * 5. Responsive & navigation
 */
import { test, expect } from '@playwright/test';

test.describe('Full Journey — Landing Page', () => {
  test('landing page loads with hero and CTA', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/MFHelper|Grow Your Wealth/i);

    const hero = page.locator('text=Grow Your Wealth').first();
    await expect(hero).toBeVisible();

    const ctaBtn = page.locator('a').filter({ hasText: /Get Started|Start Planning/i }).first();
    await expect(ctaBtn).toBeVisible();

    const nav = page.locator('nav, .navbar').first();
    await expect(nav).toBeVisible();
  });
});

test.describe('Full Journey — Auth', () => {
  test('auth page accessible from landing', async ({ page }) => {
    await page.goto('/');
    const signInLink = page.locator('a').filter({ hasText: /Sign In|Login|Log In/i }).first();
    await expect(signInLink).toBeVisible();

    await signInLink.click();
    await expect(page).toHaveURL(/auth/);
  });

  test('can switch between signin and signup tabs', async ({ page }) => {
    await page.goto('/auth.html');
    await page.waitForLoadState('domcontentloaded');

    // Start on sign-in tab — tabs use button.tab-btn
    const signinTab = page.locator('button.tab-btn').filter({ hasText: /Sign In/i }).first();
    await expect(signinTab).toBeVisible();

    // Switch to signup
    const signupTab = page.locator('button.tab-btn').filter({ hasText: /Sign Up/i }).first();
    await signupTab.click();

    // Signup form should now be visible with a name field
    const signupForm = page.locator('#signupForm, .signup-form, .tab-content.active').first();
    await expect(signupForm).toBeVisible();
  });
});

test.describe('Full Journey — Dashboard Structure', () => {
  test('dashboard page loads with all required sections', async ({ page }) => {
    await page.addInitScript(() => localStorage.clear());
    await page.goto('/dashboard.html');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    // Correct element IDs from dashboard.html source
    for (const sel of ['#dashboardContent', '#noData', '#uploadModal',
      '#performanceChart', '#riskChart',
      '#totalInvested', '#totalCurrent', '#totalGain', '#totalReturn']) {
      expect(await page.locator(sel).count(), `${sel} exists`).toBeGreaterThan(0);
    }

    // Sections present in page text
    const bodyText = await page.textContent('body') || '';
    for (const section of ['Market Cap', 'Investment Style', 'Overlap', 'Rebalancing']) {
      expect(bodyText, `Page should mention "${section}"`).toContain(section);
    }
  });
});

test.describe('Full Journey — Objective Assessment', () => {
  test('OBJECTIVE: Assess if style + cap analysis needs are met', async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    const bodyText = await page.textContent('body') || '';

    // Check: Market cap allocation analysis exists
    const hasCapAnalysis = bodyText.includes('Market Cap') && bodyText.includes('Large Cap');
    console.log('Market cap analysis section exists:', hasCapAnalysis);
    expect(hasCapAnalysis).toBe(true);

    // Check: Investment style analysis exists
    const hasStyleAnalysis = bodyText.includes('Investment Style') && bodyText.includes('GARP');
    console.log('Investment style analysis exists:', hasStyleAnalysis);
    expect(hasStyleAnalysis).toBe(true);

    // Check: Style guide explains each style
    const styles = ['GARP', 'Momentum', 'Quality Growth', 'Value', 'Passive', 'Blend', 'Sectoral'];
    const missingStyles = styles.filter(s => !bodyText.includes(s));
    console.log('Missing style descriptions:', missingStyles.length > 0 ? missingStyles : 'None');
    expect(missingStyles).toHaveLength(0);

    // Check: Rebalancing calculator exists
    const hasRebalancer = bodyText.includes('Rebalancing') && bodyText.includes('Target');
    console.log('Rebalancing calculator exists:', hasRebalancer);
    expect(hasRebalancer).toBe(true);

    // Check: Overlap analysis referenced
    const hasOverlap = bodyText.includes('Overlap');
    console.log('Overlap analysis exists:', hasOverlap);
    expect(hasOverlap).toBe(true);

    console.log('\n=== OBJECTIVE ASSESSMENT SUMMARY ===');
    console.log('Cap analysis: ✅ | Style analysis: ✅ | Rebalancer: ✅ | Overlap: ✅');
    console.log('BUT: Dashboard rendering is broken (JS errors), so users cannot see these features.');
    console.log('See dashboard.spec.ts "Critical Rendering Bug" tests for details.');
  });
});

test.describe('Full Journey — Navigation', () => {
  test('navbar links point to correct pages', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // Check main nav links exist
    const navLinks = page.locator('nav a, .navbar a');
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(2);

    // Check for key destinations
    const allHrefs: string[] = [];
    for (let i = 0; i < count; i++) {
      const href = await navLinks.nth(i).getAttribute('href');
      if (href) allHrefs.push(href);
    }

    const hasDashboard = allHrefs.some(h => h.includes('dashboard'));
    const hasAuth = allHrefs.some(h => h.includes('auth'));
    
    expect(hasDashboard || hasAuth, 'Nav should link to dashboard or auth').toBe(true);
  });

  test('goal planning page accessible', async ({ page }) => {
    const resp = await page.goto('/goal-planning.html');
    expect(resp?.status()).toBe(200);
    await expect(page).toHaveTitle(/Goal|Plan|MFHelper/i);
  });

  test('overlap analysis page accessible', async ({ page }) => {
    const resp = await page.goto('/overlap-analysis.html');
    expect(resp?.status()).toBe(200);
  });
});
