"""
Board representation for Connect 4 game.
"""

from typing import List, Optional


class Board:
    """Represents a Connect 4 game board (6 rows × 7 columns)."""
    
    ROWS = 6
    COLS = 7
    EMPTY = 0
    PLAYER1 = 1
    PLAYER2 = 2
    
    def __init__(self, board: Optional[List[List[int]]] = None):
        """
        Initialize a new board.
        
        Args:
            board: Optional 2D list representing the board state.
                  If None, creates an empty board.
        """
        if board is None:
            self.board = [[self.EMPTY for _ in range(self.COLS)] for _ in range(self.ROWS)]
        else:
            self.board = [row[:] for row in board]  # Deep copy
    
    def get_board(self) -> List[List[int]]:
        """Get a copy of the current board state."""
        return [row[:] for row in self.board]
    
    def is_column_full(self, col: int) -> bool:
        """Check if a column is full."""
        if col < 0 or col >= self.COLS:
            return True
        return self.board[0][col] != self.EMPTY
    
    def get_next_row(self, col: int) -> Optional[int]:
        """
        Get the next available row in a column.
        
        Returns:
            Row index if column has space, None otherwise.
        """
        if col < 0 or col >= self.COLS:
            return None
        
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][col] == self.EMPTY:
                return row
        return None
    
    def place_piece(self, col: int, player: int) -> bool:
        """
        Place a piece in the specified column.
        
        Args:
            col: Column index (0-6)
            player: Player number (1 or 2)
        
        Returns:
            True if piece was placed successfully, False otherwise.
        """
        row = self.get_next_row(col)
        if row is None:
            return False
        
        self.board[row][col] = player
        return True
    
    def is_full(self) -> bool:
        """Check if the board is completely full."""
        return all(self.board[0][col] != self.EMPTY for col in range(self.COLS))
    
    def get_valid_moves(self) -> List[int]:
        """Get list of valid column indices that are not full."""
        return [col for col in range(self.COLS) if not self.is_column_full(col)]
    
    def __str__(self) -> str:
        """String representation of the board."""
        lines = []
        for row in self.board:
            line = ' '.join(str(cell) for cell in row)
            lines.append(line)
        return '\n'.join(lines)

