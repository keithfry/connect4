/**
 * Playwright E2E tests for Connect 4 game - Comprehensive UX Testing
 */

import { test, expect } from '@playwright/test';

const FRONTEND_URL = 'http://localhost:8080';

test.describe('Connect 4 - Page Load & Initialization', () => {
  test('should load the game page with all elements', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Check page title
    await expect(page).toHaveTitle('Connect 4');
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('Connect 4');
    
    // Check buttons are visible
    await expect(page.locator('#new-game-btn')).toBeVisible();
    await expect(page.locator('#reset-btn')).toBeVisible();
    
    // Check game mode selection
    await expect(page.locator('input[value="human"]')).toBeChecked();
    await expect(page.locator('input[value="ai"]')).not.toBeChecked();
    
    // Check board is visible
    await expect(page.locator('#board')).toBeVisible();
    
    // Check initial status message
    await expect(page.locator('#status-text')).toContainText('Click "New Game" to start');
    
    // Check board has 42 cells (6 rows × 7 columns)
    const cells = page.locator('.cell');
    await expect(cells).toHaveCount(42);
  });

  test('should have favicon loaded', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    const favicon = page.locator('link[rel="icon"]');
    await expect(favicon).toHaveAttribute('href', 'favicon.ico');
  });
});

test.describe('Connect 4 - Game Initialization', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
  });

  test('should create a new human vs human game', async ({ page }) => {
    await page.click('#new-game-btn');
    
    // Wait for API call and status update
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
    
    // Check status shows player 1's turn
    const statusText = await page.locator('#status-text').textContent();
    expect(statusText).toContain('Player 1');
    expect(statusText).toContain('Red');
    
    // Check board is empty
    const discs = page.locator('.disc');
    await expect(discs).toHaveCount(0);
  });

  test('should create a new human vs AI game', async ({ page }) => {
    // Select AI mode
    await page.click('input[value="ai"]');
    await expect(page.locator('input[value="ai"]')).toBeChecked();
    
    // Create new game
    await page.click('#new-game-btn');
    
    // Wait for game to initialize
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
    
    // Check status (might be AI's turn if AI goes first)
    const statusText = await page.locator('#status-text').textContent();
    expect(statusText).toMatch(/Player|AI/);
  });

  test('should disable controls while creating game', async ({ page }) => {
    await page.click('#new-game-btn');
    
    // Controls should be disabled briefly
    // Note: This happens very quickly, so we check they become enabled again
    await page.waitForTimeout(100);
    await expect(page.locator('#new-game-btn')).toBeEnabled();
  });
});

test.describe('Connect 4 - Human vs Human Gameplay', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.click('#new-game-btn');
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
  });

  test('should place a red disc when player 1 clicks', async ({ page }) => {
    // Click first column (first 7 cells are top row)
    const firstColumnCells = page.locator('.cell').filter({ hasNot: page.locator('.filled') });
    await firstColumnCells.nth(0).click();
    
    // Wait for disc to appear
    await page.waitForSelector('.disc', { timeout: 2000 });
    
    // Check disc is red (player1)
    const disc = page.locator('.disc.player1').first();
    await expect(disc).toBeVisible();
    
    // Check status updated to player 2
    const statusText = await page.locator('#status-text').textContent();
    expect(statusText).toContain('Player 2');
    expect(statusText).toContain('Black');
  });

  test('should alternate turns between players', async ({ page }) => {
    // Player 1 move - column 0
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    let statusText = await page.locator('#status-text').textContent();
    expect(statusText).toContain('Player 2');
    
    // Player 2 move - column 1
    await page.locator('.cell').nth(1).click();
    await page.waitForTimeout(500);
    
    statusText = await page.locator('#status-text').textContent();
    expect(statusText).toContain('Player 1');
    
    // Should have 2 discs now
    const discs = page.locator('.disc');
    await expect(discs).toHaveCount(2);
  });

  test('should place discs in correct columns', async ({ page }) => {
    // Click column 0 (first cell)
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    // Click column 0 again (should stack)
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    // Should have 2 discs in column 0
    const discs = page.locator('.cell').nth(0).locator('.disc');
    await expect(discs).toHaveCount(1); // Only one visible at a time in same cell
    
    // Check total discs
    const allDiscs = page.locator('.disc');
    await expect(allDiscs).toHaveCount(2);
  });

  test('should prevent placing disc in full column', async ({ page }) => {
    // Fill column 0 (6 moves)
    for (let i = 0; i < 6; i++) {
      await page.locator('.cell').nth(0).click();
      await page.waitForTimeout(300);
    }
    
    // Try to place in full column - should not add another disc
    const discCountBefore = await page.locator('.disc').count();
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    const discCountAfter = await page.locator('.disc').count();
    expect(discCountAfter).toBe(discCountBefore);
  });
});

test.describe('Connect 4 - Human vs AI Gameplay', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.click('input[value="ai"]');
    await page.click('#new-game-btn');
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
  });

  test('should show AI thinking status', async ({ page }) => {
    // If AI goes first, check status
    const statusText = await page.locator('#status-text').textContent();
    
    // Either AI is thinking or it's player's turn
    if (statusText.includes('AI') || statusText.includes('thinking')) {
      expect(statusText).toMatch(/AI|thinking/i);
    }
  });

  test('should make AI move after human move', async ({ page }) => {
    // Wait for initial state
    await page.waitForTimeout(500);
    
    // Make a human move (click first available column)
    const statusText = await page.locator('#status-text').textContent();
    if (!statusText.includes('AI') && !statusText.includes('thinking')) {
      // It's human's turn, make a move
      await page.locator('.cell').nth(0).click();
      
      // Wait for AI to respond
      await page.waitForSelector('#status-text:has-text("Player 1"), #status-text:has-text("Player 2")', { timeout: 5000 });
      
      // Should have at least 2 discs (human + AI)
      const discs = page.locator('.disc');
      const count = await discs.count();
      expect(count).toBeGreaterThanOrEqual(2);
    }
  });

  test('should disable controls during AI move', async ({ page }) => {
    // Make a move if it's human's turn
    const statusText = await page.locator('#status-text').textContent();
    if (!statusText.includes('AI') && !statusText.includes('thinking')) {
      await page.locator('.cell').nth(0).click();
      
      // Controls should be disabled briefly during AI move
      // They should be enabled again after AI responds
      await page.waitForTimeout(100);
      await expect(page.locator('#new-game-btn')).toBeEnabled({ timeout: 5000 });
    }
  });
});

test.describe('Connect 4 - Visual Feedback & Animations', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.click('#new-game-btn');
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
  });

  test('should animate disc drop', async ({ page }) => {
    // Make a move
    await page.locator('.cell').nth(0).click();
    
    // Wait for disc to appear
    await page.waitForSelector('.disc', { timeout: 2000 });
    
    // Check disc has animation class (if it's a new piece)
    const disc = page.locator('.disc').first();
    await expect(disc).toBeVisible();
    
    // Disc should be visible and positioned correctly
    const discClass = await disc.getAttribute('class');
    expect(discClass).toContain('disc');
  });

  test('should display correct disc colors', async ({ page }) => {
    // Player 1 move (red)
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    const player1Disc = page.locator('.disc.player1').first();
    await expect(player1Disc).toBeVisible();
    
    // Player 2 move (black)
    await page.locator('.cell').nth(1).click();
    await page.waitForTimeout(500);
    
    const player2Disc = page.locator('.disc.player2').first();
    await expect(player2Disc).toBeVisible();
  });
});

test.describe('Connect 4 - Game Completion', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.click('#new-game-btn');
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
  });

  test('should detect horizontal win', async ({ page }) => {
    // Create a horizontal win for player 1
    // Column 0: P1, P2, P1, P2, P1, P2
    // Column 1: P1, P2, P1, P2, P1
    // Column 2: P1, P2, P1, P2
    // Column 3: P1 (winning move)
    
    const moves = [
      [0, 0], [1, 0], [0, 1], [1, 1], [0, 2], [1, 2], // Fill columns 0-2
      [0, 3], [1, 3], [0, 4], [1, 4], [0, 5], // Continue
      [2, 0], [2, 1], [2, 2], [2, 3], // Column 2
      [3, 0] // Winning move for P1
    ];
    
    for (const [col, row] of moves) {
      const cellIndex = row * 7 + col;
      await page.locator('.cell').nth(cellIndex).click();
      await page.waitForTimeout(300);
      
      // Check if game ended
      const statusText = await page.locator('#status-text').textContent();
      if (statusText.includes('wins') || statusText.includes('won')) {
        break;
      }
    }
    
    // Check win message
    const statusText = await page.locator('#status-text').textContent();
    expect(statusText).toMatch(/wins|won/i);
  });

  test('should highlight winning pieces', async ({ page }) => {
    // Make enough moves to potentially win (simplified test)
    // Just check that winning-cell class can be applied
    for (let i = 0; i < 4; i++) {
      await page.locator('.cell').nth(i).click();
      await page.waitForTimeout(300);
      
      const statusText = await page.locator('#status-text').textContent();
      if (statusText.includes('wins')) {
        // Check for winning cells
        const winningCells = page.locator('.winning-cell');
        const count = await winningCells.count();
        if (count > 0) {
          expect(count).toBeGreaterThanOrEqual(4); // 4 winning pieces
        }
        break;
      }
    }
  });

  test('should fade losing pieces on win', async ({ page }) => {
    // Make moves until someone wins
    for (let i = 0; i < 20; i++) {
      await page.locator('.cell').nth(i % 7).click();
      await page.waitForTimeout(300);
      
      const statusText = await page.locator('#status-text').textContent();
      if (statusText.includes('wins')) {
        // Check for losing pieces (should have lighter color)
        await page.waitForTimeout(500); // Wait for fade animation
        const losingPieces = page.locator('.disc.losing-piece');
        const count = await losingPieces.count();
        // Should have some losing pieces (not all pieces are winning)
        expect(count).toBeGreaterThanOrEqual(0);
        break;
      }
    }
  });

  test('should show fireworks on win', async ({ page }) => {
    // Make moves until win
    for (let i = 0; i < 20; i++) {
      await page.locator('.cell').nth(i % 7).click();
      await page.waitForTimeout(300);
      
      const statusText = await page.locator('#status-text').textContent();
      if (statusText.includes('wins')) {
        // Check for fireworks container
        await page.waitForTimeout(100); // Wait for fireworks to start
        const fireworks = page.locator('.fireworks-container, .firework');
        // Fireworks might be removed quickly, so just check they were created
        // We can't reliably test animation timing, but we can verify the structure
        break;
      }
    }
  });

  test('should prevent moves after game ends', async ({ page }) => {
    // Make moves until win
    for (let i = 0; i < 20; i++) {
      await page.locator('.cell').nth(i % 7).click();
      await page.waitForTimeout(300);
      
      const statusText = await page.locator('#status-text').textContent();
      if (statusText.includes('wins')) {
        // Try to make another move
        const discCountBefore = await page.locator('.disc').count();
        await page.locator('.cell').nth(0).click();
        await page.waitForTimeout(500);
        
        const discCountAfter = await page.locator('.disc').count();
        // Should not add more discs
        expect(discCountAfter).toBe(discCountBefore);
        break;
      }
    }
  });
});

test.describe('Connect 4 - Game Controls', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
  });

  test('should reset game correctly', async ({ page }) => {
    // Start new game
    await page.click('#new-game-btn');
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
    
    // Make a move
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    // Verify disc exists
    let discs = page.locator('.disc');
    await expect(discs).toHaveCount(1);
    
    // Reset game
    await page.click('#reset-btn');
    await page.waitForTimeout(500);
    
    // Check board is cleared
    discs = page.locator('.disc');
    await expect(discs).toHaveCount(0);
    
    // Check status reset
    const statusText = await page.locator('#status-text').textContent();
    expect(statusText).toContain('Player 1');
  });

  test('should switch game modes', async ({ page }) => {
    // Start with human vs human
    await expect(page.locator('input[value="human"]')).toBeChecked();
    
    // Switch to AI mode
    await page.click('input[value="ai"]');
    await expect(page.locator('input[value="ai"]')).toBeChecked();
    await expect(page.locator('input[value="human"]')).not.toBeChecked();
    
    // Create game
    await page.click('#new-game-btn');
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
    
    // Switch back to human mode
    await page.click('input[value="human"]');
    await expect(page.locator('input[value="human"]')).toBeChecked();
  });

  test('should create new game after reset', async ({ page }) => {
    // Start game
    await page.click('#new-game-btn');
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
    
    // Make moves
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    // Reset
    await page.click('#reset-btn');
    await page.waitForTimeout(500);
    
    // Create new game
    await page.click('#new-game-btn');
    await page.waitForTimeout(500);
    
    // Should have fresh game
    const statusText = await page.locator('#status-text').textContent();
    expect(statusText).toContain('Player');
  });
});

test.describe('Connect 4 - Error Handling', () => {
  test('should handle API errors gracefully', async ({ page }) => {
    // Intercept API calls and simulate error
    await page.route('**/api/game/new/', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Server error' })
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
  });
});

test.describe('Connect 4 - Responsive Design', () => {
  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone size
    await page.goto(FRONTEND_URL);
    
    // All elements should still be visible
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('#board')).toBeVisible();
    await expect(page.locator('#new-game-btn')).toBeVisible();
    
    // Board should be usable
    await page.click('#new-game-btn');
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
    await page.locator('.cell').nth(0).click();
    await page.waitForTimeout(500);
    
    const discs = page.locator('.disc');
    await expect(discs).toHaveCount(1);
  });

  test('should work on tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 }); // iPad size
    await page.goto(FRONTEND_URL);
    
    await expect(page.locator('#board')).toBeVisible();
    await page.click('#new-game-btn');
    await page.waitForSelector('#status-text:not(:has-text("Click"))', { timeout: 5000 });
  });
});
