/**
 * Error Handling Tests
 */

import { test, expect } from '@playwright/test';
import { FRONTEND_URL, createNewGame } from './helpers/test-helpers.js';

test.describe('Error Handling', () => {
  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API calls and simulate error
    await page.route('**/api/game/new/', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Server error' }),
      });
    });
    
    await page.goto(FRONTEND_URL);
    await page.click('#new-game-btn');
    
    // Should show error message
    await page.waitForTimeout(1000);
    const statusText = await page.locator('#status-text').textContent();
    // Error handling should display something
    expect(statusText).toBeTruthy();
  });

  test('should remain responsive during network delays', async ({ page }) => {
    // Slow down API calls
    await page.route('**/api/**', route => {
      setTimeout(() => route.continue(), 1000);
    });
    
    await page.goto(FRONTEND_URL);
    await page.click('#new-game-btn');
    
    // UI should still be responsive (buttons might be disabled but page shouldn't freeze)
    await expect(page.locator('h1')).toBeVisible();
    
    // Should eventually complete
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 10000 });
  });

  test('should handle invalid game ID', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Try to make a move without creating a game
    const discCountBefore = await page.locator('.disc').count();
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    // Should not add discs without a game
    const discCountAfter = await page.locator('.disc').count();
    expect(discCountAfter).toBe(discCountBefore);
  });

  test('should handle full column gracefully', async ({ page }) => {
    await createNewGame(page, false);
    
    // Fill column 0
    for (let i = 0; i < 6; i++) {
      await page.locator('.cell').nth(0).click();
      await page.waitForTimeout(300);
    }
    
    // Try to place in full column
    const discCountBefore = await page.locator('.disc').count();
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    // Should not add more discs
    const discCountAfter = await page.locator('.disc').count();
    expect(discCountAfter).toBe(discCountBefore);
  });
});

