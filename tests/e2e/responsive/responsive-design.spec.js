/**
 * Responsive Design Tests
 */

import { test, expect } from '@playwright/test';
import {
  FRONTEND_URL,
  createNewGame,
  makeMove,
  getDiscCount,
} from '../helpers/test-helpers.js';

test.describe('Responsive Design', () => {
  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone size
    await page.goto(FRONTEND_URL);
    
    // All elements should still be visible
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('#board')).toBeVisible();
    await expect(page.locator('#new-game-btn')).toBeVisible();
    
    // Board should be usable
    await createNewGame(page, false);
    await makeMove(page, 0);
    await page.waitForTimeout(500);
    
    const discs = await getDiscCount(page);
    expect(discs).toBeGreaterThanOrEqual(1);
  });

  test('should work on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad size
    await page.goto(FRONTEND_URL);
    
    await expect(page.locator('#board')).toBeVisible();
    await createNewGame(page, false);
    await page.waitForTimeout(500);
    
    const status = await page.locator('#status-text').textContent();
    expect(status).toContain('Player');
  });

  test('should maintain layout on different screen sizes', async ({ page }) => {
    const viewports = [
      { width: 375, height: 667 },   // Mobile
      { width: 768, height: 1024 },  // Tablet
      { width: 1920, height: 1080 }, // Desktop
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.goto(FRONTEND_URL);
      
      // Board should always be visible
      await expect(page.locator('#board')).toBeVisible();
      
      // Controls should always be accessible
      await expect(page.locator('#new-game-btn')).toBeVisible();
      await expect(page.locator('#reset-btn')).toBeVisible();
    }
  });

  test('should handle touch interactions on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(FRONTEND_URL);
    await createNewGame(page, false);
    
    // Use click (works on mobile viewports too, simulates touch)
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    const discs = await getDiscCount(page);
    expect(discs).toBeGreaterThanOrEqual(1);
  });
});

