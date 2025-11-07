"""
Storage layer for game records.
"""

import json
import os
from pathlib import Path
from typing import Optional
from .game_data import GameRecord


class GameStorage:
    """Handles storage and retrieval of game records."""
    
    def __init__(self, storage_dir: str = "game_data"):
        """
        Initialize storage.
        
        Args:
            storage_dir: Directory to store game records.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def save_game(self, game_record: GameRecord) -> bool:
        """
        Save a game record to disk.
        
        Args:
            game_record: GameRecord instance to save
        
        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            file_path = self.storage_dir / f"{game_record.game_id}.json"
            with open(file_path, 'w') as f:
                json.dump(game_record.model_dump(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game record: {e}")
            return False
    
    def load_game(self, game_id: str) -> Optional[GameRecord]:
        """
        Load a game record from disk.
        
        Args:
            game_id: Game ID to load
        
        Returns:
            GameRecord instance if found, None otherwise.
        """
        try:
            file_path = self.storage_dir / f"{game_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            return GameRecord(**data)
        except Exception as e:
            print(f"Error loading game record: {e}")
            return None

