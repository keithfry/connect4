/**
 * UI state management and event handling.
 */

class GameUI {
    constructor() {
        this.statusElement = document.getElementById('status-text');
        this.newGameBtn = document.getElementById('new-game-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.gameModeRadios = document.querySelectorAll('input[name="game-mode"]');
        
        this.setupEventListeners();
    }
    
    /**
     * Set up event listeners for UI controls.
     */
    setupEventListeners() {
        this.newGameBtn.addEventListener('click', () => {
            const event = new CustomEvent('newGame', {
                detail: { hasAI: this.getGameMode() === 'ai' }
            });
            document.dispatchEvent(event);
        });
        
        this.resetBtn.addEventListener('click', () => {
            document.dispatchEvent(new CustomEvent('resetGame'));
        });
    }
    
    /**
     * Get the selected game mode.
     * @returns {string} 'human' or 'ai'
     */
    getGameMode() {
        const selected = document.querySelector('input[name="game-mode"]:checked');
        return selected ? selected.value : 'human';
    }
    
    /**
     * Update the status text.
     * @param {string} text - Status text to display
     */
    updateStatus(text) {
        this.statusElement.textContent = text;
    }
    
    /**
     * Update status based on game state.
     * @param {Object} state - Game state object
     */
    updateGameStatus(state) {
        if (state.status === 'won') {
            const playerColor = state.winner === 1 ? 'Red' : 'Black';
            this.updateStatus(`Player ${state.winner} (${playerColor}) wins!`);
        } else if (state.status === 'draw') {
            this.updateStatus('Game ended in a draw!');
        } else if (state.status === 'playing') {
            const playerColor = state.current_player === 1 ? 'Red' : 'Black';
            if (state.has_ai && state.current_player === state.ai_player) {
                this.updateStatus(`AI (Player ${state.current_player}) is thinking...`);
            } else {
                this.updateStatus(`Player ${state.current_player}'s turn (${playerColor})`);
            }
        }
    }
    
    /**
     * Enable or disable game controls.
     * @param {boolean} enabled - Whether controls should be enabled
     */
    setControlsEnabled(enabled) {
        this.newGameBtn.disabled = !enabled;
        this.resetBtn.disabled = !enabled;
        this.gameModeRadios.forEach(radio => {
            radio.disabled = !enabled;
        });
    }
}

