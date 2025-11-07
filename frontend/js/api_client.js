/**
 * API client for communicating with the Django backend.
 */

const API_BASE_URL = 'http://localhost:8000';

class APIClient {
    /**
     * Create a new game.
     * @param {boolean} hasAI - Whether the game has an AI player
     * @param {number} aiPlayer - Which player is AI (1 or 2)
     * @returns {Promise<Object>} Game state
     */
    async createGame(hasAI = false, aiPlayer = 2) {
        const response = await fetch(`${API_BASE_URL}/api/game/new/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                has_ai: hasAI,
                ai_player: aiPlayer,
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create game');
        }
        
        return await response.json();
    }
    
    /**
     * Make a move in the game.
     * @param {string} gameId - Game ID
     * @param {number} column - Column index (0-6)
     * @returns {Promise<Object>} Updated game state
     */
    async makeMove(gameId, column) {
        const response = await fetch(`${API_BASE_URL}/api/game/${gameId}/move/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                column: column,
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to make move');
        }
        
        return await response.json();
    }
    
    /**
     * Get current game state.
     * @param {string} gameId - Game ID
     * @returns {Promise<Object>} Game state
     */
    async getState(gameId) {
        const response = await fetch(`${API_BASE_URL}/api/game/${gameId}/state/`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to get game state');
        }
        
        return await response.json();
    }
    
    /**
     * Request an AI move.
     * @param {string} gameId - Game ID
     * @returns {Promise<Object>} Updated game state
     */
    async aiMove(gameId) {
        const response = await fetch(`${API_BASE_URL}/api/game/${gameId}/ai-move/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to get AI move');
        }
        
        return await response.json();
    }
    
    /**
     * Reset the game.
     * @param {string} gameId - Game ID
     * @returns {Promise<Object>} Reset game state
     */
    async resetGame(gameId) {
        const response = await fetch(`${API_BASE_URL}/api/game/${gameId}/reset/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to reset game');
        }
        
        return await response.json();
    }
}

// Export singleton instance
const apiClient = new APIClient();

