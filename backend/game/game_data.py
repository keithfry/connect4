"""
Pydantic models for game data recording.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MoveRecord(BaseModel):
    """Record of a single move."""
    move_number: int
    player: int
    column: int
    board_state: List[List[int]]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class GameRecord(BaseModel):
    """Complete record of a game."""
    game_id: str
    start_time: str
    end_time: Optional[str] = None
    moves: List[MoveRecord] = Field(default_factory=list)
    result: Optional[str] = None  # 'player1_won', 'player2_won', 'draw'
    winner: Optional[int] = None
    final_board: Optional[List[List[int]]] = None

