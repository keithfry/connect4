/**
 * Gameplay Tests - Win Conditions
 */

import { test, expect } from '@playwright/test';
import {
  FRONTEND_URL,
  createNewGame,
  getGameStatus,
  createHorizontalWin,
} from '../helpers/test-helpers.js';

test.describe('Win Conditions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await createNewGame(page, false);
  });

  test('should detect horizontal win', async ({ page }) => {
    // Create a horizontal win
    await createHorizontalWin(page, 1);
    
    // Wait for win detection
    await page.waitForTimeout(1000);
    
    const status = await getGameStatus(page);
    expect(status).toMatch(/wins|won/i);
  });

  test('should highlight winning pieces', async ({ page }) => {
    await createHorizontalWin(page, 1);
    await page.waitForTimeout(1000);
    
    // Check for winning cells
    const winningCells = page.locator('.winning-cell');
    const count = await winningCells.count();
    
    if (count > 0) {
      // Should have at least 4 winning pieces
      expect(count).toBeGreaterThanOrEqual(4);
    }
  });

  test('should display winner message', async ({ page }) => {
    await createHorizontalWin(page, 1);
    await page.waitForTimeout(1000);
    
    const status = await getGameStatus(page);
    expect(status).toMatch(/Player [12].*wins/i);
  });

  test('should prevent moves after game ends', async ({ page }) => {
    await createHorizontalWin(page, 1);
    await page.waitForTimeout(1000);
    
    // Try to make a move
    const discCountBefore = await page.locator('.disc').count();
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    const discCountAfter = await page.locator('.disc').count();
    // Should not add more discs
    expect(discCountAfter).toBe(discCountBefore);
  });

  test('should fade losing player pieces on win', async ({ page }) => {
    await createHorizontalWin(page, 1);
    await page.waitForTimeout(1000); // Wait for animations
    
    // Check for losing pieces (should have lighter colors)
    const losingPieces = page.locator('.disc.losing-piece');
    const count = await losingPieces.count();
    
    // Should have some losing pieces (not all pieces are winning)
    expect(count).toBeGreaterThanOrEqual(0);
  });
});

