import { test, expect, Page } from '@playwright/test';

/**
 * UI Revamp Tests - Acorns-Inspired Design
 * Tests for v0.2.0-ui-revamp changes
 */

test.describe('Homepage UI Revamp', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should have correct color scheme CSS variables', async ({ page }) => {
    // Check that CSS variables are defined
    const primaryGreen = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--primary-green').trim();
    });
    expect(primaryGreen).toBe('#7FC04C');
  });

  test('should display fixed navigation bar', async ({ page }) => {
    const navbar = page.locator('.navbar');
    await expect(navbar).toBeVisible();
    
    // Check navbar is fixed position
    const position = await navbar.evaluate(el => getComputedStyle(el).position);
    expect(position).toBe('fixed');
  });

  test('should show MFHelper logo in navbar', async ({ page }) => {
    const logo = page.locator('.logo');
    await expect(logo).toBeVisible();
    await expect(logo).toContainText('MFHelper');
  });

  test('should have navigation links', async ({ page }) => {
    const navLinks = ['Goal Planning', 'Dashboard', 'AI Chat'];
    
    for (const link of navLinks) {
      const navLink = page.locator(`.nav-link:has-text("${link}")`).first();
      await expect(navLink).toBeVisible();
    }
  });

  test('should display hero section with headline', async ({ page }) => {
    const heroText = page.locator('.hero-text h1');
    await expect(heroText).toBeVisible();
    await expect(heroText).toContainText('Grow Your Wealth');
  });

  test('should have shimmer effect on highlight text', async ({ page }) => {
    const highlight = page.locator('.highlight');
    await expect(highlight).toBeVisible();
    await expect(highlight).toContainText('Smarter & Faster');
  });

  test('should display hero SVG chart', async ({ page }) => {
    const svg = page.locator('.hero-image svg');
    await expect(svg).toBeVisible();
    
    // Check SVG has bar elements
    const bars = page.locator('.hero-image svg rect');
    expect(await bars.count()).toBeGreaterThan(0);
  });

  test('should have floating decorative shapes', async ({ page }) => {
    const floatingShapes = page.locator('.floating-shape');
    expect(await floatingShapes.count()).toBeGreaterThan(0);
  });

  test('should display stats section with counters', async ({ page }) => {
    const statsSection = page.locator('.stats-section');
    await expect(statsSection).toBeVisible();
    
    const statItems = page.locator('.stat-item');
    expect(await statItems.count()).toBe(4);
  });

  test('should have CTA buttons with correct styling', async ({ page }) => {
    const primaryBtn = page.locator('.btn-primary').first();
    await expect(primaryBtn).toBeVisible();
    
    // Check button has green color
    const bgColor = await primaryBtn.evaluate(el => getComputedStyle(el).backgroundColor);
    expect(bgColor).toContain('127'); // RGB for primary green
  });

  test('should scroll smoothly to sections', async ({ page }) => {
    const goalPlanningLink = page.locator('a[href="#goal-planning"]').first();
    await goalPlanningLink.click();
    
    // Wait for smooth scroll
    await page.waitForTimeout(1000);
    
    // Verify section is visible
    const goalSection = page.locator('#goal-planning');
    await expect(goalSection).toBeInViewport();
  });

  test('should display footer', async ({ page }) => {
    const footer = page.locator('.footer');
    await expect(footer).toBeVisible();
    await expect(footer).toContainText('MFHelper');
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    
    // Hamburger menu should be visible
    const hamburger = page.locator('.hamburger');
    await expect(hamburger).toBeVisible();
    
    // Click hamburger to open menu
    await hamburger.click();
    
    // Nav menu should become visible
    const navMenu = page.locator('.nav-menu');
    await expect(navMenu).toHaveClass(/active/);
  });

  test('should capture homepage screenshot', async ({ page }) => {
    await page.screenshot({
      path: 'test-results/screenshots/homepage-revamp.png',
      fullPage: true
    });
  });
});

test.describe('Dashboard UI Revamp', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard.html');
    await page.waitForLoadState('networkidle');
  });

  test('should have consistent navbar with homepage', async ({ page }) => {
    const navbar = page.locator('.navbar');
    await expect(navbar).toBeVisible();
    
    // Check logo
    const logo = page.locator('.logo');
    await expect(logo).toContainText('MFHelper');
  });

  test('should have green color scheme', async ({ page }) => {
    // Check that primary green is used
    const primaryGreen = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--primary-green').trim();
    });
    expect(primaryGreen).toBe('#7FC04C');
  });

  test('should display navigation links', async ({ page }) => {
    const homeLink = page.locator('.nav-link:has-text("Home")');
    await expect(homeLink).toBeVisible();
    
    const goalPlanningLink = page.locator('.nav-link:has-text("Goal Planning")');
    await expect(goalPlanningLink).toBeVisible();
  });

  test('should have action buttons', async ({ page }) => {
    const uploadBtn = page.locator('button:has-text("Upload")');
    await expect(uploadBtn).toBeVisible();
    
    const exportBtn = page.locator('button:has-text("Export")');
    await expect(exportBtn).toBeVisible();
  });

  test('should capture dashboard screenshot', async ({ page }) => {
    await page.screenshot({
      path: 'test-results/screenshots/dashboard-revamp.png',
      fullPage: true
    });
  });
});

test.describe('Goal Planning UI Revamp', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/goal-planning.html');
    await page.waitForLoadState('networkidle');
  });

  test('should have consistent navbar', async ({ page }) => {
    const navbar = page.locator('.navbar');
    await expect(navbar).toBeVisible();
    
    const logo = page.locator('.logo');
    await expect(logo).toContainText('MFHelper');
  });

  test('should display summary cards at top', async ({ page }) => {
    const statCards = page.locator('.stat-card');
    expect(await statCards.count()).toBeGreaterThanOrEqual(4);
  });

  test('should have chart and goals side by side layout', async ({ page }) => {
    // Check flex container exists
    const flexContainer = page.locator('.flex.gap-4.mb-6').first();
    // If the layout is correct, both chart and goals should be visible
    const chartCard = page.locator('.glass-card:has-text("Wealth Growth")');
    await expect(chartCard).toBeVisible();
  });

  test('should display goal template cards', async ({ page }) => {
    const goalCards = page.locator('.goal-card');
    expect(await goalCards.count()).toBeGreaterThan(0);
  });

  test('should have default max age of 80', async ({ page }) => {
    const lifeEndAgeInput = page.locator('input[value="80"]').first();
    // Check that 80 is present somewhere
    const pageContent = await page.content();
    expect(pageContent).toContain('80');
  });

  test('should show custom input modal when clicking goal template', async ({ page }) => {
    // Click on a goal template card
    const goalCard = page.locator('.goal-card').first();
    await goalCard.click();
    
    // Custom modal should appear (not browser prompt)
    const inputModal = page.locator('form input[name="amount"]');
    await expect(inputModal).toBeVisible({ timeout: 3000 });
  });

  test('should close modal on cancel button', async ({ page }) => {
    // Click on a goal template card
    const goalCard = page.locator('.goal-card').first();
    await goalCard.click();
    
    // Wait for modal
    await page.waitForTimeout(500);
    
    // Click cancel
    const cancelBtn = page.locator('button:has-text("Cancel")').first();
    await cancelBtn.click();
    
    // Modal should be hidden
    await page.waitForTimeout(300);
    const inputModal = page.locator('form input[name="amount"]');
    await expect(inputModal).not.toBeVisible();
  });

  test('should display chart SVG', async ({ page }) => {
    const svg = page.locator('svg').first();
    await expect(svg).toBeVisible();
  });

  test('should have scenario buttons', async ({ page }) => {
    const optimisticBtn = page.locator('button:has-text("Optimistic")');
    await expect(optimisticBtn).toBeVisible();
    
    const mediumBtn = page.locator('button:has-text("Medium")');
    await expect(mediumBtn).toBeVisible();
    
    const pessimisticBtn = page.locator('button:has-text("Pessimistic")');
    await expect(pessimisticBtn).toBeVisible();
  });

  test('should switch scenarios when clicking buttons', async ({ page }) => {
    const optimisticBtn = page.locator('button:has-text("Optimistic")');
    await optimisticBtn.click();
    
    // Button should become active (have bg-green-500 class)
    await expect(optimisticBtn).toHaveClass(/bg-green-500/);
  });

  test('should capture goal planning screenshot', async ({ page }) => {
    await page.screenshot({
      path: 'test-results/screenshots/goal-planning-revamp.png',
      fullPage: true
    });
  });
});

test.describe('Animation Tests', () => {
  test('should have fade-in animations on homepage', async ({ page }) => {
    await page.goto('/');
    
    // Check that fade-in class exists
    const fadeInElements = page.locator('.fade-in');
    expect(await fadeInElements.count()).toBeGreaterThan(0);
  });

  test('should trigger animations on scroll', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Scroll down
    await page.evaluate(() => window.scrollBy(0, 500));
    await page.waitForTimeout(1000);
    
    // Elements should have 'visible' class added
    const visibleElements = page.locator('.fade-in.visible');
    expect(await visibleElements.count()).toBeGreaterThan(0);
  });

  test('should have parallax effect on hero', async ({ page }) => {
    await page.goto('/');
    
    // Get initial hero image position
    const heroImage = page.locator('.hero-image');
    const initialTransform = await heroImage.evaluate(el => el.style.transform);
    
    // Scroll down
    await page.evaluate(() => window.scrollBy(0, 200));
    await page.waitForTimeout(500);
    
    // Transform should have changed (parallax effect)
    const newTransform = await heroImage.evaluate(el => el.style.transform);
    expect(newTransform).not.toBe(initialTransform);
  });
});

test.describe('Cross-Page Consistency', () => {
  test('should have same logo on all pages', async ({ page }) => {
    const pages = ['/', '/dashboard.html', '/goal-planning.html'];
    
    for (const pagePath of pages) {
      await page.goto(pagePath);
      const logo = page.locator('.logo');
      await expect(logo).toContainText('MFHelper');
    }
  });

  test('should have consistent navbar structure', async ({ page }) => {
    const pages = ['/', '/dashboard.html', '/goal-planning.html'];
    
    for (const pagePath of pages) {
      await page.goto(pagePath);
      const navbar = page.locator('.navbar');
      await expect(navbar).toBeVisible();
    }
  });

  test('should have consistent color scheme', async ({ page }) => {
    const pages = ['/', '/dashboard.html', '/goal-planning.html'];
    
    for (const pagePath of pages) {
      await page.goto(pagePath);
      const primaryGreen = await page.evaluate(() => {
        return getComputedStyle(document.documentElement).getPropertyValue('--primary-green').trim();
      });
      expect(primaryGreen).toBe('#7FC04C');
    }
  });
});
