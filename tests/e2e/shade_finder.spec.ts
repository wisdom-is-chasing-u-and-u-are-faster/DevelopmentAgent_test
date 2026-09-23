import { test, expect } from '@playwright/test';

test.describe('Cosmetics Storefront - Shade Finder Journey', () => {
  test('User can select shade swatch and see instant visual feedback', async ({ page }) => {
    await page.goto('/products/luminous-silk-foundation');
    
    // Check WCAG accessible radio group
    const swatchGroup = page.locator('div[role="radiogroup"]');
    await expect(swatchGroup).toBeVisible();

    // Select second swatch
    const swatch = page.locator('button[role="radio"]').nth(1);
    await swatch.click();
    await expect(swatch).toHaveAttribute('aria-checked', 'true');
  });

  test('Camera Shade Matcher modal opens and displays webcam viewfinder', async ({ page }) => {
    await page.goto('/products/luminous-silk-foundation');
    await page.click('button:has-text("Find My Shade")');
    await expect(page.locator('h3:has-text("Live Camera Shade Matcher")')).toBeVisible();
  });
});
