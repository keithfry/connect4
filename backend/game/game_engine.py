"""
Core game engine for Connect 4.
"""

from typing import Optional
from .board import Board
from .win_checker import WinChecker


class GameEngine:
    """Manages the core game logic."""
    
    PLAYING = 'playing'
    WON = 'won'
    DRAW = 'draw'
    
    def __init__(self):
        """Initialize a new game."""
        self.board = Board()
        self.current_player = Board.PLAYER1
        self.status = self.PLAYING
        self.winner = None
    
    def get_state(self) -> dict:
        """
        Get the current game state.
        
        Returns:
            Dictionary containing board, current_player, status, winner, and winning_positions.
        """
        winning_positions = None
        if self.status == self.WON and self.winner:
            winning_positions = WinChecker.get_winning_positions(self.board)
        
        return {
            'board': self.board.get_board(),
            'current_player': self.current_player,
            'status': self.status,
            'winner': self.winner,
            'winning_positions': winning_positions,
        }
    
    def make_move(self, col: int) -> dict:
        """
        Make a move in the specified column.
        
        Args:
            col: Column index (0-6)
        
        Returns:
            Dictionary with success status and updated game state.
        """
        if self.status != self.PLAYING:
            return {
                'success': False,
                'error': 'Game is not in playing state',
                'state': self.get_state()
            }
        
        if col < 0 or col >= Board.COLS:
            return {
                'success': False,
                'error': 'Invalid column',
                'state': self.get_state()
            }
        
        if self.board.is_column_full(col):
            return {
                'success': False,
                'error': 'Column is full',
                'state': self.get_state()
            }
        
        # Place the piece
        self.board.place_piece(col, self.current_player)
        
        # Check for winner
        winner = WinChecker.check_winner(self.board)
        if winner:
            self.status = self.WON
            self.winner = winner
        elif self.board.is_full():
            self.status = self.DRAW
            self.winner = None
        else:
            # Switch player
            self.current_player = Board.PLAYER2 if self.current_player == Board.PLAYER1 else Board.PLAYER1
        
        return {
            'success': True,
            'state': self.get_state()
        }
    
    def reset(self):
        """Reset the game to initial state."""
        self.board = Board()
        self.current_player = Board.PLAYER1
        self.status = self.PLAYING
        self.winner = None
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.status != self.PLAYING

