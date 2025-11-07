/**
 * Board rendering and visual updates.
 */

class BoardRenderer {
    constructor(boardElement) {
        this.boardElement = boardElement;
        this.ROWS = 6;
        this.COLS = 7;
        this.previousBoard = null; // Track previous board state
        this.init();
    }
    
    /**
     * Initialize the board DOM structure.
     */
    init() {
        this.boardElement.innerHTML = '';
        this.previousBoard = null; // Reset previous board state
        for (let row = 0; row < this.ROWS; row++) {
            for (let col = 0; col < this.COLS; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                this.boardElement.appendChild(cell);
            }
        }
    }
    
    /**
     * Render the board state.
     * @param {Array<Array<number>>} board - 2D array representing the board
     * @param {Array<Array<number>>} winningCells - Optional array of [row, col] winning positions
     * @param {number} winner - Optional winner player number (1 or 2)
     */
    render(board, winningCells = [], winner = null) {
        const cells = this.boardElement.querySelectorAll('.cell');
        const winningSet = new Set(winningCells.map(([r, c]) => `${r},${c}`));
        const hasWinner = winner !== null && winningCells.length > 0;
        
        // Find the newly placed piece (if any)
        let newPiece = null;
        if (this.previousBoard) {
            for (let row = 0; row < this.ROWS; row++) {
                for (let col = 0; col < this.COLS; col++) {
                    if (this.previousBoard[row][col] === 0 && board[row][col] !== 0) {
                        newPiece = { row, col, player: board[row][col] };
                        break;
                    }
                }
                if (newPiece) break;
            }
        }
        
        cells.forEach((cell, index) => {
            const row = Math.floor(index / this.COLS);
            const col = index % this.COLS;
            const value = board[row][col];
            const existingDisc = cell.querySelector('.disc');
            
            // Check if this is the newly placed piece
            const isNewPiece = newPiece && newPiece.row === row && newPiece.col === col;
            
            // Only update if the value changed or if this is a new piece
            const previousValue = this.previousBoard ? this.previousBoard[row][col] : 0;
            const valueChanged = previousValue !== value;
            
            if (valueChanged) {
                // Remove existing disc if present
                if (existingDisc) {
                    existingDisc.remove();
                }
                
                // Remove winning class
                cell.classList.remove('winning-cell');
                
                // Add disc if cell is filled
                if (value !== 0) {
                    cell.classList.add('filled');
                    const disc = document.createElement('div');
                    disc.className = `disc player${value}`;
                    
                    // Only add animation class for the newly placed piece
                    if (isNewPiece) {
                        disc.classList.add('animate-drop');
                    }
                    
                    // Apply lighter styling to all pieces when there's a winner,
                    // EXCEPT the winning 4 pieces
                    const isWinningPiece = winningSet.has(`${row},${col}`);
                    if (hasWinner && !isWinningPiece) {
                        disc.classList.add('losing-piece');
                    }
                    
                    cell.appendChild(disc);
                    
                    // Highlight winning cells
                    if (isWinningPiece) {
                        cell.classList.add('winning-cell');
                    }
                } else {
                    cell.classList.remove('filled');
                }
            } else if (value !== 0 && existingDisc) {
                // Update winning cell highlighting for existing pieces
                const isWinningPiece = winningSet.has(`${row},${col}`);
                if (isWinningPiece) {
                    cell.classList.add('winning-cell');
                } else {
                    cell.classList.remove('winning-cell');
                }
                
                // Apply lighter styling to all pieces when there's a winner,
                // EXCEPT the winning 4 pieces
                if (hasWinner && !isWinningPiece) {
                    existingDisc.classList.add('losing-piece');
                } else {
                    existingDisc.classList.remove('losing-piece');
                }
            }
        });
        
        // Store current board state for next render
        this.previousBoard = board.map(row => [...row]);
    }
    
    /**
     * Animate a disc drop.
     * @param {number} row - Row index
     * @param {number} col - Column index
     * @param {number} player - Player number (1 or 2)
     */
    animateDrop(row, col, player) {
        const cellIndex = row * this.COLS + col;
        const cells = this.boardElement.querySelectorAll('.cell');
        const cell = cells[cellIndex];
        
        // Create disc
        const disc = document.createElement('div');
        disc.className = `disc player${player}`;
        cell.appendChild(disc);
        cell.classList.add('filled');
    }
    
    /**
     * Enable or disable column hover effects.
     * @param {boolean} enabled - Whether to enable hover
     */
    setHoverEnabled(enabled) {
        const cells = this.boardElement.querySelectorAll('.cell');
        cells.forEach(cell => {
            if (enabled) {
                cell.style.pointerEvents = 'auto';
            } else {
                cell.style.pointerEvents = 'none';
            }
        });
    }
    
    /**
     * Create firework animation over the board.
     */
    createFireworks() {
        const container = this.boardElement.parentElement; // board-container
        const fireworksContainer = document.createElement('div');
        fireworksContainer.className = 'fireworks-container';
        
        // Get board dimensions
        const boardRect = this.boardElement.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        // Position and size the container to cover the board
        const offsetX = boardRect.left - containerRect.left;
        const offsetY = boardRect.top - containerRect.top;
        fireworksContainer.style.left = `${offsetX}px`;
        fireworksContainer.style.top = `${offsetY}px`;
        fireworksContainer.style.width = `${boardRect.width}px`;
        fireworksContainer.style.height = `${boardRect.height}px`;
        
        container.appendChild(fireworksContainer);
        
        // Create multiple fireworks
        for (let i = 0; i < 20; i++) {
            setTimeout(() => {
                this.createFirework(fireworksContainer, boardRect.width, boardRect.height);
            }, i * 100);
        }
        
        // Remove fireworks container after animation
        setTimeout(() => {
            if (fireworksContainer.parentNode) {
                fireworksContainer.remove();
            }
        }, 3000);
    }
    
    /**
     * Create a single firework.
     * @param {HTMLElement} container - Container element for the firework
     * @param {number} width - Width of the board area
     * @param {number} height - Height of the board area
     */
    createFirework(container, width, height) {
        const firework = document.createElement('div');
        firework.className = 'firework';
        
        // Random position within the container
        const x = Math.random() * width;
        const y = Math.random() * height;
        
        firework.style.left = `${x}px`;
        firework.style.top = `${y}px`;
        
        // Random color
        const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b', '#6c5ce7'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        firework.style.setProperty('--firework-color', color);
        
        container.appendChild(firework);
        
        // Remove after animation
        setTimeout(() => {
            if (firework.parentNode) {
                firework.remove();
            }
        }, 1500);
    }
}

