/**
 * Main game controller coordinating all components.
 */

class GameController {
    constructor() {
        this.currentGameId = null;
        this.currentState = null;
        this.boardRenderer = new BoardRenderer(document.getElementById('board'));
        this.gameUI = new GameUI();
        
        this.setupEventListeners();
    }
    
    /**
     * Set up event listeners.
     */
    setupEventListeners() {
        // New game event
        document.addEventListener('newGame', async (e) => {
            await this.startNewGame(e.detail.hasAI);
        });
        
        // Reset game event
        document.addEventListener('resetGame', async () => {
            if (this.currentGameId) {
                await this.resetGame();
            }
        });
        
        // Cell click handler
        this.boardRenderer.boardElement.addEventListener('click', async (e) => {
            const cell = e.target.closest('.cell');
            if (cell && !cell.classList.contains('filled')) {
                const col = parseInt(cell.dataset.col);
                await this.handleCellClick(col);
            }
        });
    }
    
    /**
     * Start a new game.
     * @param {boolean} hasAI - Whether to include an AI player
     */
    async startNewGame(hasAI = false) {
        try {
            this.gameUI.setControlsEnabled(false);
            this.gameUI.updateStatus('Creating new game...');
            
            const state = await apiClient.createGame(hasAI, 2);
            this.currentGameId = state.game_id;
            this.currentState = state;
            
            this.boardRenderer.init();
            this.updateDisplay(state);
            this.gameUI.setControlsEnabled(true);
            
            // If AI goes first, make AI move
            if (hasAI && state.current_player === 2) {
                await this.makeAIMove();
            }
        } catch (error) {
            this.gameUI.updateStatus(`Error: ${error.message}`);
            this.gameUI.setControlsEnabled(true);
        }
    }
    
    /**
     * Reset the current game.
     */
    async resetGame() {
        if (!this.currentGameId) return;
        
        try {
            this.gameUI.setControlsEnabled(false);
            const state = await apiClient.resetGame(this.currentGameId);
            this.currentState = state;
            this.boardRenderer.init();
            this.updateDisplay(state);
            this.gameUI.setControlsEnabled(true);
            
            // If AI goes first, make AI move
            if (state.has_ai && state.current_player === state.ai_player) {
                await this.makeAIMove();
            }
        } catch (error) {
            this.gameUI.updateStatus(`Error: ${error.message}`);
            this.gameUI.setControlsEnabled(true);
        }
    }
    
    /**
     * Handle cell click.
     * @param {number} col - Column index
     */
    async handleCellClick(col) {
        if (!this.currentGameId || !this.currentState) return;
        if (this.currentState.status !== 'playing') return;
        
        // Don't allow moves if it's AI's turn
        if (this.currentState.has_ai && this.currentState.current_player === this.currentState.ai_player) {
            return;
        }
        
        try {
            this.gameUI.setControlsEnabled(false);
            const state = await apiClient.makeMove(this.currentGameId, col);
            this.currentState = state;
            
            // Find the row where the piece was placed
            const oldBoard = this.currentState.board;
            // We'll update after getting the new state
            this.updateDisplay(state);
            
            // If game is still playing and it's AI's turn, make AI move
            if (state.status === 'playing' && state.has_ai && state.current_player === state.ai_player) {
                setTimeout(() => this.makeAIMove(), 500); // Small delay for visual feedback
            } else {
                this.gameUI.setControlsEnabled(true);
            }
        } catch (error) {
            this.gameUI.updateStatus(`Error: ${error.message}`);
            this.gameUI.setControlsEnabled(true);
        }
    }
    
    /**
     * Make an AI move.
     */
    async makeAIMove() {
        if (!this.currentGameId) return;
        
        try {
            this.gameUI.updateStatus('AI is thinking...');
            const state = await apiClient.aiMove(this.currentGameId);
            this.currentState = state;
            this.updateDisplay(state);
            this.gameUI.setControlsEnabled(true);
        } catch (error) {
            this.gameUI.updateStatus(`Error: ${error.message}`);
            this.gameUI.setControlsEnabled(true);
        }
    }
    
    /**
     * Update the display with current game state.
     * @param {Object} state - Game state
     */
    updateDisplay(state) {
        const wasPlaying = this.currentState && this.currentState.status === 'playing';
        const isWon = state.status === 'won';
        
        // Trigger fireworks if game just ended with a win
        if (wasPlaying && isWon && state.winner) {
            // Small delay to ensure DOM is updated
            setTimeout(() => {
                this.boardRenderer.createFireworks();
            }, 100);
        }
        
        // Get winning positions from state (if available)
        const winningPositions = state.winning_positions || [];
        this.boardRenderer.render(state.board, winningPositions, state.winner);
        this.gameUI.updateGameStatus(state);
    }
}

