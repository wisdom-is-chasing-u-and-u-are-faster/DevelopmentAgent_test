import { test, expect } from '@playwright/test';

test.describe('Customer Subscriptions Portal E2E', () => {
  test('Customer can view active auto-replenishment regimen and skip next shipment', async ({ page }) => {
    await page.goto('/account/subscriptions');
    await expect(page.locator('h1')).toContainText('Your Beauty Regimen');

    const skipButton = page.locator('button:has-text("Skip Refill")').first();
    await skipButton.click();

    // Validate optimistic update
    await expect(page.locator('text=SKIPPED')).toBeVisible();
  });

  test('Customer can open Swap Shade modal and update upcoming refill', async ({ page }) => {
    await page.goto('/account/subscriptions');
    await page.click('button:has-text("Swap Shade")');

    await expect(page.locator('h3:has-text("Swap Refill Shade")')).toBeVisible();
    await page.click('text=Warm Olive #30');
    await page.click('button:has-text("Confirm Swap")');

    await expect(page.locator('text=Warm Olive #30')).toBeVisible();
  });
});
