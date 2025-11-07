"""
Win condition detection for Connect 4.
"""

from typing import Optional, Tuple
from .board import Board


class WinChecker:
    """Checks for win conditions in Connect 4."""
    
    WIN_LENGTH = 4
    
    @staticmethod
    def check_winner(board: Board) -> Optional[int]:
        """
        Check if there's a winner.
        
        Args:
            board: Board instance to check
        
        Returns:
            Player number (1 or 2) if there's a winner, None otherwise.
        """
        board_state = board.get_board()
        
        # Check horizontal
        for row in range(Board.ROWS):
            for col in range(Board.COLS - WinChecker.WIN_LENGTH + 1):
                player = board_state[row][col]
                if player != Board.EMPTY:
                    if all(board_state[row][col + i] == player for i in range(WinChecker.WIN_LENGTH)):
                        return player
        
        # Check vertical
        for row in range(Board.ROWS - WinChecker.WIN_LENGTH + 1):
            for col in range(Board.COLS):
                player = board_state[row][col]
                if player != Board.EMPTY:
                    if all(board_state[row + i][col] == player for i in range(WinChecker.WIN_LENGTH)):
                        return player
        
        # Check diagonal (top-left to bottom-right)
        for row in range(Board.ROWS - WinChecker.WIN_LENGTH + 1):
            for col in range(Board.COLS - WinChecker.WIN_LENGTH + 1):
                player = board_state[row][col]
                if player != Board.EMPTY:
                    if all(board_state[row + i][col + i] == player for i in range(WinChecker.WIN_LENGTH)):
                        return player
        
        # Check diagonal (top-right to bottom-left)
        for row in range(Board.ROWS - WinChecker.WIN_LENGTH + 1):
            for col in range(WinChecker.WIN_LENGTH - 1, Board.COLS):
                player = board_state[row][col]
                if player != Board.EMPTY:
                    if all(board_state[row + i][col - i] == player for i in range(WinChecker.WIN_LENGTH)):
                        return player
        
        return None
    
    @staticmethod
    def get_winning_positions(board: Board) -> Optional[list]:
        """
        Get the positions of the winning line.
        
        Args:
            board: Board instance to check
        
        Returns:
            List of (row, col) tuples if there's a winner, None otherwise.
        """
        board_state = board.get_board()
        
        # Check horizontal
        for row in range(Board.ROWS):
            for col in range(Board.COLS - WinChecker.WIN_LENGTH + 1):
                player = board_state[row][col]
                if player != Board.EMPTY:
                    if all(board_state[row][col + i] == player for i in range(WinChecker.WIN_LENGTH)):
                        return [(row, col + i) for i in range(WinChecker.WIN_LENGTH)]
        
        # Check vertical
        for row in range(Board.ROWS - WinChecker.WIN_LENGTH + 1):
            for col in range(Board.COLS):
                player = board_state[row][col]
                if player != Board.EMPTY:
                    if all(board_state[row + i][col] == player for i in range(WinChecker.WIN_LENGTH)):
                        return [(row + i, col) for i in range(WinChecker.WIN_LENGTH)]
        
        # Check diagonal (top-left to bottom-right)
        for row in range(Board.ROWS - WinChecker.WIN_LENGTH + 1):
            for col in range(Board.COLS - WinChecker.WIN_LENGTH + 1):
                player = board_state[row][col]
                if player != Board.EMPTY:
                    if all(board_state[row + i][col + i] == player for i in range(WinChecker.WIN_LENGTH)):
                        return [(row + i, col + i) for i in range(WinChecker.WIN_LENGTH)]
        
        # Check diagonal (top-right to bottom-left)
        for row in range(Board.ROWS - WinChecker.WIN_LENGTH + 1):
            for col in range(WinChecker.WIN_LENGTH - 1, Board.COLS):
                player = board_state[row][col]
                if player != Board.EMPTY:
                    if all(board_state[row + i][col - i] == player for i in range(WinChecker.WIN_LENGTH)):
                        return [(row + i, col - i) for i in range(WinChecker.WIN_LENGTH)]
        
        return None

