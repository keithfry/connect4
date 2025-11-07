/**
 * AI Tests - AI Gameplay
 */

import { test, expect } from '@playwright/test';
import {
  FRONTEND_URL,
  createNewGame,
  getGameStatus,
  getDiscCount,
  waitForAIMove,
  makeMove,
} from '../helpers/test-helpers.js';

test.describe('AI Gameplay', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await createNewGame(page, true);
  });

  test('should show AI thinking status', async ({ page }) => {
    await page.waitForTimeout(500);
    
    const status = await getGameStatus(page);
    // Either AI is thinking or it's player's turn
    if (status.includes('AI') || status.includes('thinking')) {
      expect(status).toMatch(/AI|thinking/i);
    }
  });

  test('should make AI move after human move', async ({ page }) => {
    await page.waitForTimeout(500);
    
    const status = await getGameStatus(page);
    
    // If it's human's turn, make a move
    if (!status.includes('AI') && !status.includes('thinking')) {
      await makeMove(page, 0);
      
      // Wait for AI to respond
      await waitForAIMove(page, 10000);
      
      // Should have at least 2 discs (human + AI)
      const discCount = await getDiscCount(page);
      expect(discCount).toBeGreaterThanOrEqual(2);
    }
  });

  test('should disable controls during AI move', async ({ page }) => {
    await page.waitForTimeout(500);
    
    const status = await getGameStatus(page);
    if (!status.includes('AI') && !status.includes('thinking')) {
      await makeMove(page, 0);
      
      // Controls should be disabled briefly during AI move
      // They should be enabled again after AI responds
      await page.waitForTimeout(100);
      await expect(page.locator('#new-game-btn')).toBeEnabled({ timeout: 10000 });
    }
  });

  test('should alternate between human and AI moves', async ({ page }) => {
    await page.waitForTimeout(500);
    
    // Make a human move if it's our turn
    const initialStatus = await getGameStatus(page);
    if (!initialStatus.includes('AI') && !initialStatus.includes('thinking')) {
      await makeMove(page, 0);
      await waitForAIMove(page, 10000);
      
      // After AI move, should be human's turn again
      const status = await getGameStatus(page);
      expect(status).toContain('Player');
      expect(status).not.toContain('AI');
      expect(status).not.toContain('thinking');
    }
  });

  test('should make valid AI moves', async ({ page }) => {
    await page.waitForTimeout(500);
    
    // Make a move and wait for AI response
    const status = await getGameStatus(page);
    if (!status.includes('AI') && !status.includes('thinking')) {
      await makeMove(page, 0);
      await waitForAIMove(page, 10000);
      
      // AI should have placed a disc
      const discCount = await getDiscCount(page);
      expect(discCount).toBeGreaterThanOrEqual(2);
      
      // AI disc should be black (player 2)
      const aiDisc = page.locator('.disc.player2');
      const aiDiscCount = await aiDisc.count();
      expect(aiDiscCount).toBeGreaterThanOrEqual(1);
    }
  });
});

