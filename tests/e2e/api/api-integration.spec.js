/**
 * API Integration Tests
 */

import { test, expect } from '@playwright/test';
import { API_BASE_URL, FRONTEND_URL } from '../helpers/test-helpers.js';

test.describe('API Integration', () => {
  test('should create game via API', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/game/new/`, {
      data: {
        has_ai: false,
        ai_player: 2,
      },
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('game_id');
    expect(data).toHaveProperty('board');
    expect(data).toHaveProperty('status', 'playing');
    expect(data).toHaveProperty('current_player');
  });

  test('should make move via API', async ({ request }) => {
    // Create game
    const createResponse = await request.post(`${API_BASE_URL}/api/game/new/`, {
      data: { has_ai: false },
    });
    const gameData = await createResponse.json();
    const gameId = gameData.game_id;
    
    // Make a move
    const moveResponse = await request.post(`${API_BASE_URL}/api/game/${gameId}/move/`, {
      data: { column: 0 },
    });
    
    expect(moveResponse.ok()).toBeTruthy();
    const moveData = await moveResponse.json();
    expect(moveData).toHaveProperty('board');
    expect(moveData).toHaveProperty('current_player');
    expect(moveData.current_player).toBe(2); // Should switch to player 2
  });

  test('should get game state via API', async ({ request }) => {
    // Create game
    const createResponse = await request.post(`${API_BASE_URL}/api/game/new/`, {
      data: { has_ai: false },
    });
    const gameData = await createResponse.json();
    const gameId = gameData.game_id;
    
    // Get state
    const stateResponse = await request.get(`${API_BASE_URL}/api/game/${gameId}/state/`);
    
    expect(stateResponse.ok()).toBeTruthy();
    const stateData = await stateResponse.json();
    expect(stateData).toHaveProperty('game_id', gameId);
    expect(stateData).toHaveProperty('board');
    expect(stateData).toHaveProperty('status');
  });

  test('should handle invalid move via API', async ({ request }) => {
    // Create game
    const createResponse = await request.post(`${API_BASE_URL}/api/game/new/`, {
      data: { has_ai: false },
    });
    const gameData = await createResponse.json();
    const gameId = gameData.game_id;
    
    // Try invalid column
    const moveResponse = await request.post(`${API_BASE_URL}/api/game/${gameId}/move/`, {
      data: { column: 10 }, // Invalid column
    });
    
    expect(moveResponse.ok()).toBeFalsy();
    const errorData = await moveResponse.json();
    expect(errorData).toHaveProperty('error');
  });

  test('should reset game via API', async ({ request }) => {
    // Create game and make a move
    const createResponse = await request.post(`${API_BASE_URL}/api/game/new/`, {
      data: { has_ai: false },
    });
    const gameData = await createResponse.json();
    const gameId = gameData.game_id;
    
    await request.post(`${API_BASE_URL}/api/game/${gameId}/move/`, {
      data: { column: 0 },
    });
    
    // Reset game
    const resetResponse = await request.post(`${API_BASE_URL}/api/game/${gameId}/reset/`);
    
    expect(resetResponse.ok()).toBeTruthy();
    const resetData = await resetResponse.json();
    expect(resetData).toHaveProperty('board');
    // Board should be empty (all zeros)
    const board = resetData.board;
    const isEmpty = board.every(row => row.every(cell => cell === 0));
    expect(isEmpty).toBeTruthy();
  });

  test('should handle AI move via API', async ({ request }) => {
    // Create game with AI
    const createResponse = await request.post(`${API_BASE_URL}/api/game/new/`, {
      data: { has_ai: true, ai_player: 2 },
    });
    const gameData = await createResponse.json();
    const gameId = gameData.game_id;
    
    // Make human move if it's player 1's turn
    if (gameData.current_player === 1) {
      await request.post(`${API_BASE_URL}/api/game/${gameId}/move/`, {
        data: { column: 0 },
      });
    }
    
    // Request AI move
    const aiResponse = await request.post(`${API_BASE_URL}/api/game/${gameId}/ai-move/`);
    
    expect(aiResponse.ok()).toBeTruthy();
    const aiData = await aiResponse.json();
    expect(aiData).toHaveProperty('board');
    expect(aiData).toHaveProperty('current_player');
  });
});

