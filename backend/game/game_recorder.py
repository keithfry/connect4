"""
Game recording system for training data collection.
"""

from datetime import datetime
from typing import Optional
from .game_engine import GameEngine
from .game_data import GameRecord, MoveRecord
from .storage import GameStorage


class GameRecorder:
    """Records game actions for neural network training."""
    
    def __init__(self, storage_dir: str = "game_data"):
        """
        Initialize game recorder.
        
        Args:
            storage_dir: Directory to store game records.
        """
        self.storage = GameStorage(storage_dir)
        self.current_game: Optional[GameRecord] = None
    
    def start_game(self, game_id: Optional[str] = None) -> str:
        """
        Start recording a new game.
        
        Args:
            game_id: Optional game ID. If None, generates timestamp-based ID.
        
        Returns:
            Game ID.
        """
        if game_id is None:
            game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.current_game = GameRecord(
            game_id=game_id,
            start_time=datetime.now().isoformat(),
            moves=[]
        )
        return game_id
    
    def record_move(self, player: int, column: int, board_state: list, move_number: int):
        """
        Record a move.
        
        Args:
            player: Player number (1 or 2)
            column: Column where piece was placed
            board_state: Current board state after the move
            move_number: Sequential move number
        """
        if self.current_game is None:
            return
        
        move = MoveRecord(
            move_number=move_number,
            player=player,
            column=column,
            board_state=[row[:] for row in board_state]  # Deep copy
        )
        self.current_game.moves.append(move)
    
    def end_game(self, game_engine: GameEngine, save: bool = True) -> Optional[GameRecord]:
        """
        End the current game and save the record.
        
        Args:
            game_engine: GameEngine instance to get final state
            save: Whether to save to disk
        
        Returns:
            GameRecord instance.
        """
        if self.current_game is None:
            return None
        
        state = game_engine.get_state()
        self.current_game.end_time = datetime.now().isoformat()
        self.current_game.final_board = state['board']
        
        if state['status'] == 'won':
            self.current_game.winner = state['winner']
            self.current_game.result = f"player{state['winner']}_won"
        elif state['status'] == 'draw':
            self.current_game.result = 'draw'
            self.current_game.winner = None
        
        if save:
            self.storage.save_game(self.current_game)
        
        game_record = self.current_game
        self.current_game = None
        return game_record

