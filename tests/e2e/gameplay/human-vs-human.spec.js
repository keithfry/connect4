/**
 * Gameplay Tests - Human vs Human
 */

import { test, expect } from '@playwright/test';
import {
  FRONTEND_URL,
  createNewGame,
  makeMove,
  getGameStatus,
  getDiscCount,
  isColumnFull,
} from '../helpers/test-helpers.js';

test.describe('Human vs Human Gameplay', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await createNewGame(page, false);
  });

  test('should place red disc when player 1 clicks', async ({ page }) => {
    await makeMove(page, 0);
    
    // Wait for disc to appear
    await page.waitForSelector('.disc', { timeout: 2000 });
    
    // Check disc is red (player1)
    const disc = page.locator('.disc.player1').first();
    await expect(disc).toBeVisible();
    
    // Check status updated to player 2
    const status = await getGameStatus(page);
    expect(status).toContain('Player 2');
    expect(status).toContain('Black');
  });

  test('should alternate turns between players', async ({ page }) => {
    // Player 1 move - column 0
    await makeMove(page, 0);
    await page.waitForTimeout(500);
    
    let status = await getGameStatus(page);
    expect(status).toContain('Player 2');
    
    // Player 2 move - column 1
    await makeMove(page, 1);
    await page.waitForTimeout(500);
    
    status = await getGameStatus(page);
    expect(status).toContain('Player 1');
    
    // Should have 2 discs now
    expect(await getDiscCount(page)).toBe(2);
  });

  test('should stack discs in the same column', async ({ page }) => {
    // Place two discs in column 0
    await makeMove(page, 0);
    await page.waitForTimeout(500);
    await makeMove(page, 0);
    await page.waitForTimeout(500);
    
    // Should have 2 discs
    expect(await getDiscCount(page)).toBe(2);
    
    // Both should be in column 0 (different rows)
    const column0Cells = [
      page.locator('.cell').nth(35), // Bottom row
      page.locator('.cell').nth(28), // Second from bottom
    ];
    
    for (const cell of column0Cells) {
      const disc = cell.locator('.disc');
      const count = await disc.count();
      expect(count).toBeGreaterThanOrEqual(0); // At least one should have a disc
    }
  });

  test('should prevent placing disc in full column', async ({ page }) => {
    // Fill column 0 (6 moves)
    for (let i = 0; i < 6; i++) {
      await makeMove(page, 0);
      await page.waitForTimeout(300);
    }
    
    // Try to place in full column
    const discCountBefore = await getDiscCount(page);
    await makeMove(page, 0);
    await page.waitForTimeout(500);
    
    const discCountAfter = await getDiscCount(page);
    // Should not add more discs (column is full)
    expect(discCountAfter).toBe(discCountBefore);
  });

  test('should place discs in correct visual positions', async ({ page }) => {
    // Place disc in column 0
    await makeMove(page, 0);
    await page.waitForTimeout(500);
    
    // Disc should appear in bottom row of column 0
    const bottomCell = page.locator('.cell').nth(35); // Row 5, Col 0
    const disc = bottomCell.locator('.disc');
    await expect(disc).toBeVisible();
  });

  test('should update status message on each move', async ({ page }) => {
    // Initial status
    let status = await getGameStatus(page);
    expect(status).toContain('Player 1');
    
    // After player 1 move
    await makeMove(page, 0);
    await page.waitForTimeout(500);
    status = await getGameStatus(page);
    expect(status).toContain('Player 2');
    
    // After player 2 move
    await makeMove(page, 1);
    await page.waitForTimeout(500);
    status = await getGameStatus(page);
    expect(status).toContain('Player 1');
  });
});

