"""
AI strategy interface and implementations.
"""

from typing import Protocol
from ..board import Board


class AIStrategy(Protocol):
    """Protocol for AI strategies."""
    
    def get_move(self, board: Board, current_player: int) -> int:
        """
        Get the best move for the current player.
        
        Args:
            board: Current board state
            current_player: Current player (1 or 2)
        
        Returns:
            Column index for best move.
        """
        ...

