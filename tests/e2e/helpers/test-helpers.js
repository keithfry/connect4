/**
 * Test helpers and utilities for Connect 4 E2E tests
 */

export const FRONTEND_URL = 'http://localhost:8080';
export const API_BASE_URL = 'http://localhost:8000';

/**
 * Wait for game to be initialized
 */
export async function waitForGameInitialized(page) {
  // Wait for status to show a player's turn (not "Creating new game..." or "Click...")
  await page.waitForFunction(
    () => {
      const statusText = document.querySelector('#status-text')?.textContent || '';
      return statusText.includes('Player') || statusText.includes('wins') || statusText.includes('draw');
    },
    { timeout: 5000 }
  );
}

/**
 * Create a new game
 */
export async function createNewGame(page, hasAI = false) {
  if (hasAI) {
    await page.click('input[value="ai"]');
  } else {
    await page.click('input[value="human"]');
  }
  await page.click('#new-game-btn');
  await waitForGameInitialized(page);
}

/**
 * Make a move in a specific column
 */
export async function makeMove(page, column) {
  const cellIndex = column; // Top row, column index
  await page.locator('.cell').nth(cellIndex).click();
  await page.waitForTimeout(500); // Wait for move to complete
}

/**
 * Get current game status text
 */
export async function getGameStatus(page) {
  return await page.locator('#status-text').textContent();
}

/**
 * Get number of discs on the board
 */
export async function getDiscCount(page) {
  return await page.locator('.disc').count();
}

/**
 * Check if a column is full (by trying to click it)
 */
export async function isColumnFull(page, column) {
  const cell = page.locator('.cell').nth(column);
  const isFilled = await cell.locator('.filled').count() > 0;
  // Check if top cell is filled (column is full)
  return isFilled && (await cell.locator('.disc').count()) > 0;
}

/**
 * Wait for AI move to complete
 */
export async function waitForAIMove(page, timeout = 5000) {
  // Wait for status to not contain "thinking" or "AI"
  await page.waitForFunction(
    () => {
      const statusElement = document.querySelector('#status-text');
      if (!statusElement) return false;
      const text = statusElement.textContent || '';
      return !text.includes('thinking') && !text.includes('AI');
    },
    { timeout }
  );
}

/**
 * Create a horizontal win for a player
 * Strategy: Build pieces in columns 0-3, alternating players, then complete horizontal 4-in-a-row
 * 
 * Example pattern for horizontal win in bottom row (row 5):
 * - P1: col 0 (row 5)
 * - P2: col 0 (row 4) 
 * - P1: col 1 (row 5)
 * - P2: col 1 (row 4)
 * - P1: col 2 (row 5)
 * - P2: col 2 (row 4)
 * - P1: col 3 (row 5) - WIN! (4 horizontal pieces)
 */
export async function createHorizontalWin(page, player = 1) {
  // Pattern to create horizontal win: stack in pairs, then complete the row
  // Columns: [0, 0, 1, 1, 2, 2, 3] creates horizontal win in bottom row
  const columns = [0, 0, 1, 1, 2, 2, 3];
  
  for (const col of columns) {
    // Click any cell in the column (top row is fine, piece will fall to bottom available space)
    const topRowCellIndex = col; // Top row cells are indices 0-6
    await page.locator('.cell').nth(topRowCellIndex).click();
    await page.waitForTimeout(400);
    
    // Check if game ended
    const status = await getGameStatus(page);
    if (status.includes('wins') || status.includes('won')) {
      break;
    }
  }
}

/**
 * Fill the board to create a draw scenario
 */
export async function createDraw(page) {
  // Fill board column by column
  for (let col = 0; col < 7; col++) {
    for (let row = 0; row < 6; row++) {
      const cellIndex = row * 7 + col;
      const cell = page.locator('.cell').nth(cellIndex);
      const isFilled = await cell.locator('.filled').count() === 0;
      
      if (isFilled) {
        await cell.click();
        await page.waitForTimeout(200);
        
        const status = await getGameStatus(page);
        if (status.includes('draw') || status.includes('wins')) {
          return;
        }
      }
    }
  }
}

