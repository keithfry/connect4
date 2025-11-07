"""
Pydantic models for API request/response validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class NewGameRequest(BaseModel):
    """Request to create a new game."""
    has_ai: bool = False
    ai_player: int = Field(default=2, ge=1, le=2)


class MoveRequest(BaseModel):
    """Request to make a move."""
    column: int = Field(ge=0, le=6)


class GameStateResponse(BaseModel):
    """Game state response."""
    game_id: str
    board: List[List[int]]
    current_player: int
    status: str
    winner: Optional[int] = None
    has_ai: bool = False
    ai_player: Optional[int] = None
    winning_positions: Optional[List[List[int]]] = None


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    state: Optional[GameStateResponse] = None

