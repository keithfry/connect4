/**
 * UI Tests - Page Load and Initialization
 */

import { test, expect } from '@playwright/test';
import { FRONTEND_URL } from '../helpers/test-helpers.js';

test.describe('Page Load and Initialization', () => {
  test('should load the game page with correct title', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await expect(page).toHaveTitle('Connect 4');
  });

  test('should display all required UI elements', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Main heading
    await expect(page.locator('h1')).toContainText('Connect 4');
    await expect(page.locator('h1')).toBeVisible();
    
    // Control buttons
    await expect(page.locator('#new-game-btn')).toBeVisible();
    await expect(page.locator('#reset-btn')).toBeVisible();
    
    // Game mode selection
    await expect(page.locator('input[value="human"]')).toBeVisible();
    await expect(page.locator('input[value="ai"]')).toBeVisible();
    
    // Board container
    await expect(page.locator('#board')).toBeVisible();
    await expect(page.locator('.board-container')).toBeVisible();
    
    // Status display
    await expect(page.locator('#status-text')).toBeVisible();
  });

  test('should have correct initial state', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Human vs Human mode should be selected by default
    await expect(page.locator('input[value="human"]')).toBeChecked();
    await expect(page.locator('input[value="ai"]')).not.toBeChecked();
    
    // Initial status message
    await expect(page.locator('#status-text')).toContainText('Click "New Game" to start');
    
    // Board should be empty
    const discs = page.locator('.disc');
    await expect(discs).toHaveCount(0);
  });

  test('should have correct board structure', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Board should have 42 cells (6 rows × 7 columns)
    const cells = page.locator('.cell');
    await expect(cells).toHaveCount(42);
    
    // Board should have yellow background
    const board = page.locator('.board');
    const backgroundColor = await board.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor;
    });
    expect(backgroundColor).toContain('255, 215, 0'); // Yellow RGB
  });

  test('should load favicon', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    const favicon = page.locator('link[rel="icon"]');
    await expect(favicon).toHaveAttribute('href', 'favicon.ico');
    
    // Verify favicon loads
    const faviconHref = await favicon.getAttribute('href');
    const response = await page.goto(`${FRONTEND_URL}/${faviconHref}`);
    expect(response?.status()).toBe(200);
  });

  test('should have responsive layout', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Check that board is centered
    const boardContainer = page.locator('.board-container');
    const containerStyles = await boardContainer.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        display: styles.display,
        justifyContent: styles.justifyContent,
      };
    });
    
    expect(containerStyles.display).toBe('flex');
  });
});

