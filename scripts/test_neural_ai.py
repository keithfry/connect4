#!/usr/bin/env python
"""
Test neural AI to see what moves it's predicting.
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.game.ai.neural_ai import NeuralAI
from backend.game.board import Board
from backend.game.game_engine import GameEngine


def test_neural_ai():
    """Test neural AI predictions on various board states."""
    print("Loading Neural AI...")
    ai = NeuralAI(model_version="v1")
    
    if ai.model is None:
        print("ERROR: Model not loaded!")
        return
    
    print(f"Model loaded successfully!")
    print(f"Model input shape: {ai.model.input_shape}")
    
    # Test on empty board
    print("\n" + "="*60)
    print("Test 1: Empty board (Player 1's turn)")
    print("="*60)
    board = Board()
    move = ai.get_move(board, 1)
    print(f"Predicted move: Column {move}")
    
    # Get probabilities
    from backend.game.ai.preprocessing import board_to_input
    from backend.game.ai.model import MaskedMoveModel
    board_input = board_to_input(board.get_board(), 1)
    predicted_column, probabilities = ai.masked_model.predict(board_input, board)
    print(f"Move probabilities: {probabilities}")
    print(f"Best move: Column {predicted_column} (prob: {probabilities[predicted_column]:.4f})")
    
    # Test on board with some pieces
    print("\n" + "="*60)
    print("Test 2: Board with some pieces (Player 2's turn)")
    print("="*60)
    engine = GameEngine()
    engine.make_move(3)  # Player 1 moves center
    engine.make_move(3)  # Player 2 moves center
    engine.make_move(2)  # Player 1 moves left of center
    engine.make_move(2)  # Player 2 moves left of center
    
    board = Board(engine.board.get_board())
    move = ai.get_move(board, engine.current_player)
    print(f"Current board state:")
    print(board)
    print(f"\nPredicted move: Column {move}")
    
    board_input = board_to_input(board.get_board(), engine.current_player)
    predicted_column, probabilities = ai.masked_model.predict(board_input, board)
    print(f"Move probabilities: {probabilities}")
    print(f"Best move: Column {predicted_column} (prob: {probabilities[predicted_column]:.4f})")
    
    # Test multiple moves to see pattern
    print("\n" + "="*60)
    print("Test 3: Multiple moves from empty board")
    print("="*60)
    engine = GameEngine()
    moves_made = []
    for i in range(10):
        current_player = engine.current_player
        board = Board(engine.board.get_board())
        move = ai.get_move(board, current_player)
        moves_made.append(move)
        result = engine.make_move(move)
        if not result['success']:
            print(f"Move {i+1} failed!")
            break
        print(f"Move {i+1}: Player {current_player} -> Column {move}")
        if engine.status != GameEngine.PLAYING:
            print(f"Game ended: {engine.status}")
            break
    
    print(f"\nFirst 10 moves: {moves_made}")
    
    # Check if it's always the same column
    if len(set(moves_made)) == 1:
        print(f"⚠️  WARNING: AI always plays the same column ({moves_made[0]})!")
    else:
        print(f"✓ AI uses {len(set(moves_made))} different columns")


if __name__ == '__main__':
    test_neural_ai()

