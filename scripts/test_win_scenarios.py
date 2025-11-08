#!/usr/bin/env python
"""
Test the neural network AI on obvious win/block scenarios.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.game.ai.neural_ai import NeuralAI
from backend.game.board import Board
from backend.game.win_checker import WinChecker
from backend.game.ai.gpu_config import configure_gpu
from backend.game.ai.preprocessing import board_to_input
import numpy as np


def print_board(board):
    """Print board state."""
    board_state = board.get_board()
    print("Board state:")
    for row in board_state:
        print("  " + " ".join(str(cell) for cell in row))
    print()


def test_scenario(name, board_state, current_player, expected_move=None):
    """Test a specific scenario."""
    print(f"\n{'='*60}")
    print(f"Scenario: {name}")
    print(f"{'='*60}")
    
    board = Board()
    board._board = [row[:] for row in board_state]
    
    print_board(board)
    print(f"Current player: {current_player}")
    
    # Check for wins
    win_checker = WinChecker()
    winner = win_checker.check_winner(board)
    if winner:
        print(f"⚠️  Board already has a winner: Player {winner}")
    
    # Check for immediate wins
    for col in range(7):
        if not board.is_column_full(col):
            test_board = Board()
            test_board._board = [row[:] for row in board_state]
            if test_board.place_piece(col, current_player):
                test_win_checker = WinChecker()
                if test_win_checker.check_winner(test_board) == current_player:
                    print(f"🎯 IMMEDIATE WIN available in column {col}!")
    
    # Check for blocks needed
    opponent = 1 if current_player == 2 else 2
    for col in range(7):
        if not board.is_column_full(col):
            test_board = Board()
            test_board._board = [row[:] for row in board_state]
            if test_board.place_piece(col, opponent):
                test_win_checker = WinChecker()
                if test_win_checker.check_winner(test_board) == opponent:
                    print(f"🛡️  BLOCK NEEDED in column {col} (opponent would win)!")
    
    # Get AI prediction
    ai = NeuralAI(model_version="v1")
    move = ai.get_move(board, current_player)
    
    # Get probabilities
    board_input = board_to_input(board.get_board(), current_player)
    _, probs = ai.masked_model.predict(board_input, board)
    
    print(f"\nAI Prediction:")
    print(f"  Selected move: Column {move}")
    print(f"  Probabilities:")
    for col in range(7):
        marker = " ← SELECTED" if col == move else ""
        if expected_move and col == expected_move:
            marker += " ← EXPECTED"
        print(f"    Column {col}: {probs[col]:.4f}{marker}")
    
    if expected_move and move != expected_move:
        print(f"\n❌ FAILED: Expected column {expected_move}, got {move}")
    elif expected_move:
        print(f"\n✓ PASSED: Correctly selected column {expected_move}")
    
    return move


def main():
    configure_gpu()
    
    print("Testing Neural AI on win/block scenarios...")
    
    # Scenario 1: Immediate win (horizontal)
    # Player 1 has: [1, 1, 1, 0] - should play column 3
    test_scenario(
        "Immediate Win (Horizontal)",
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0],  # Player 1 needs column 3
        ],
        current_player=1,
        expected_move=3
    )
    
    # Scenario 2: Block opponent win (horizontal)
    # Player 2 has: [2, 2, 2, 0] - Player 1 should block column 3
    test_scenario(
        "Block Opponent Win (Horizontal)",
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [2, 2, 2, 0, 0, 0, 0],  # Player 2 about to win, Player 1 should block
        ],
        current_player=1,
        expected_move=3
    )
    
    # Scenario 3: Immediate win (vertical)
    # Player 1 has 3 in column 0 - should play column 0
    test_scenario(
        "Immediate Win (Vertical)",
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],  # Player 1 needs column 0
        ],
        current_player=1,
        expected_move=0
    )
    
    # Scenario 4: Block opponent win (vertical)
    test_scenario(
        "Block Opponent Win (Vertical)",
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0, 0],  # Player 2 about to win, Player 1 should block
        ],
        current_player=1,
        expected_move=0
    )
    
    # Scenario 5: Two threats (win > block)
    # Player 1 can win OR block - should win
    test_scenario(
        "Win vs Block (Should Win)",
        [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 2, 2, 2],  # Player 1 can win (col 3) or block (col 6) - should win
        ],
        current_player=1,
        expected_move=3
    )


if __name__ == '__main__':
    main()

