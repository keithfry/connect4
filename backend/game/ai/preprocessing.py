"""
Preprocessing utilities for converting board states to neural network inputs.
"""

import numpy as np
from typing import List, Tuple
from ..board import Board


def board_to_input(board_state: List[List[int]], current_player: int = None) -> np.ndarray:
    """
    Convert board state to neural network input format.
    
    Args:
        board_state: 6x7 board state (list of lists)
        current_player: Current player (1 or 2), optional. If provided, adds as third channel.
    
    Returns:
        numpy array of shape (6, 7, 2) or (6, 7, 3) if current_player is provided
    """
    board_array = np.array(board_state, dtype=np.float32)
    
    # Create two-channel representation
    # Channel 1: Player 1 pieces (1 where player 1 has piece, 0 otherwise)
    # Channel 2: Player 2 pieces (1 where player 2 has piece, 0 otherwise)
    channel1 = (board_array == Board.PLAYER1).astype(np.float32)
    channel2 = (board_array == Board.PLAYER2).astype(np.float32)
    
    if current_player is not None:
        # Add third channel for current player indicator
        channel3 = np.full((6, 7), current_player, dtype=np.float32) / 2.0  # Normalize to [0.5, 1.0]
        input_array = np.stack([channel1, channel2, channel3], axis=-1)
    else:
        input_array = np.stack([channel1, channel2], axis=-1)
    
    return input_array


def create_move_mask(board: Board) -> np.ndarray:
    """
    Create a mask for valid moves (columns that are not full).
    
    Args:
        board: Board instance
    
    Returns:
        numpy array of shape (7,) with 1.0 for valid columns, 0.0 for full columns
    """
    mask = np.ones(7, dtype=np.float32)
    for col in range(Board.COLS):
        if board.is_column_full(col):
            mask[col] = 0.0
    return mask


def apply_move_mask(predictions: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Apply move mask to predictions, setting invalid moves to 0 and renormalizing.
    
    Args:
        predictions: Raw predictions from model (7 values)
        mask: Move mask (7 values, 1.0 for valid, 0.0 for invalid)
    
    Returns:
        Masked and normalized predictions
    """
    # Apply mask
    masked = predictions * mask
    
    # Renormalize to ensure probabilities sum to 1
    sum_masked = np.sum(masked)
    if sum_masked > 0:
        masked = masked / sum_masked
    else:
        # If all moves are invalid (shouldn't happen in normal play), return uniform distribution
        masked = mask / np.sum(mask) if np.sum(mask) > 0 else np.ones(7) / 7.0
    
    return masked


def prepare_batch(board_states: List[List[List[int]]], current_players: List[int] = None) -> np.ndarray:
    """
    Prepare a batch of board states for neural network input.
    
    Args:
        board_states: List of board states (each is 6x7)
        current_players: Optional list of current players for each board state
    
    Returns:
        numpy array of shape (batch_size, 6, 7, 2) or (batch_size, 6, 7, 3)
    """
    inputs = []
    for i, board_state in enumerate(board_states):
        current_player = current_players[i] if current_players is not None else None
        input_array = board_to_input(board_state, current_player)
        inputs.append(input_array)
    
    return np.array(inputs)

