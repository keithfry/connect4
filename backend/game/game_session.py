"""
Game session management.
"""

from typing import Optional, Dict
from .game_engine import GameEngine
from .game_recorder import GameRecorder
from .board import Board


class GameSession:
    """Manages a game session with recording."""
    
    def __init__(self, game_id: str, has_ai: bool = False, ai_player: int = 2):
        """
        Initialize a game session.
        
        Args:
            game_id: Unique game identifier
            has_ai: Whether this game has an AI player
            ai_player: Which player is AI (1 or 2)
        """
        self.game_id = game_id
        self.engine = GameEngine()
        self.recorder = GameRecorder()
        self.recorder.start_game(game_id)
        self.has_ai = has_ai
        self.ai_player = ai_player
        self.move_count = 0
    
    def make_move(self, column: int) -> dict:
        """
        Make a move in the game.
        
        Args:
            column: Column index (0-6)
        
        Returns:
            Dictionary with success status and game state.
        """
        result = self.engine.make_move(column)
        
        if result['success']:
            # Get the player who just made the move (before switch)
            player_who_moved = self.engine.current_player
            # The engine switches players after a move, so we need to get the previous player
            # If game is still playing, current_player is the next player
            # If game ended, current_player is still the player who just moved
            if result['state']['status'] == 'playing':
                # Game is still playing, so current_player was switched
                # The player who moved is the opposite
                player_who_moved = Board.PLAYER2 if result['state']['current_player'] == Board.PLAYER1 else Board.PLAYER1
            else:
                # Game ended, current_player is the one who just moved
                player_who_moved = result['state']['current_player']
            
            self.move_count += 1
            state = result['state']
            
            # Record the move
            self.recorder.record_move(
                player=player_who_moved,
                column=column,
                board_state=state['board'],
                move_number=self.move_count
            )
            
            # If game is over, finalize recording
            if self.engine.is_game_over():
                self.recorder.end_game(self.engine, save=True)
        
        return result
    
    def get_state(self) -> dict:
        """Get current game state."""
        state = self.engine.get_state()
        state['game_id'] = self.game_id
        state['has_ai'] = self.has_ai
        state['ai_player'] = self.ai_player
        return state
    
    def reset(self):
        """Reset the game session."""
        self.engine.reset()
        self.move_count = 0
        self.recorder.start_game(self.game_id)
    
    def is_ai_turn(self) -> bool:
        """Check if it's the AI's turn."""
        return self.has_ai and self.engine.current_player == self.ai_player

