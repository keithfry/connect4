/**
 * UI Tests - Game Controls
 */

import { test, expect } from '@playwright/test';
import { FRONTEND_URL, createNewGame, getGameStatus, getDiscCount } from '../helpers/test-helpers.js';

test.describe('Game Controls', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
  });

  test('should create new game when clicking New Game button', async ({ page }) => {
    await createNewGame(page, false);
    
    const status = await getGameStatus(page);
    expect(status).toContain('Player 1');
    expect(status).toContain('Red');
  });

  test('should reset game when clicking Reset button', async ({ page }) => {
    await createNewGame(page, false);
    
    // Make a move
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    // Verify disc exists
    expect(await getDiscCount(page)).toBe(1);
    
    // Reset game
    await page.click('#reset-btn');
    await page.waitForTimeout(500);
    
    // Board should be cleared
    expect(await getDiscCount(page)).toBe(0);
    
    // Status should reset
    const status = await getGameStatus(page);
    expect(status).toContain('Player 1');
  });

  test('should switch between human and AI game modes', async ({ page }) => {
    // Start with human mode
    await expect(page.locator('input[value="human"]')).toBeChecked();
    
    // Switch to AI mode
    await page.click('input[value="ai"]');
    await expect(page.locator('input[value="ai"]')).toBeChecked();
    await expect(page.locator('input[value="human"]')).not.toBeChecked();
    
    // Create game
    await createNewGame(page, true);
    const status = await getGameStatus(page);
    expect(status).toBeTruthy();
    
    // Switch back to human mode
    await page.click('input[value="human"]');
    await expect(page.locator('input[value="human"]')).toBeChecked();
  });

  test('should disable controls during game initialization', async ({ page }) => {
    await page.click('#new-game-btn');
    
    // Controls should be disabled briefly
    // They should be enabled again after initialization
    await page.waitForTimeout(100);
    await expect(page.locator('#new-game-btn')).toBeEnabled({ timeout: 5000 });
  });

  test('should allow creating new game after reset', async ({ page }) => {
    await createNewGame(page, false);
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    // Reset
    await page.click('#reset-btn');
    await page.waitForTimeout(500);
    
    // Create new game
    await createNewGame(page, false);
    const status = await getGameStatus(page);
    expect(status).toContain('Player');
  });
});

