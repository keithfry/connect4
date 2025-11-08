#!/usr/bin/env python
"""
Investigate the most repeated board state to understand why it appears so often.
"""

import sys
from pathlib import Path
import numpy as np
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.game.ai.data_generator import load_training_data


def investigate_repeated_board(data_path, num_samples=30000):
    """Find and analyze the most repeated board state."""
    print(f"Loading training data from: {data_path}")
    
    X, y = load_training_data(data_path)
    X_sample = X[:num_samples]
    y_sample = y[:num_samples]
    moves = np.argmax(y_sample, axis=1)
    
    # Find most repeated board
    board_counts = Counter()
    board_indices = {}
    
    for i, board in enumerate(X_sample):
        board_tuple = tuple(board.flatten())
        board_counts[board_tuple] += 1
        if board_tuple not in board_indices:
            board_indices[board_tuple] = []
        board_indices[board_tuple].append(i)
    
    # Get most repeated board
    most_repeated = board_counts.most_common(1)[0]
    board_tuple, count = most_repeated
    indices = board_indices[board_tuple]
    
    print(f"\nMost repeated board state appears {count} times")
    print(f"First appears at index: {indices[0]}")
    print(f"All indices: {indices[:20]}..." if len(indices) > 20 else f"All indices: {indices}")
    
    # Reconstruct the board
    board_array = np.array(board_tuple).reshape(X_sample[0].shape)
    board_2d = np.sum(board_array[:, :, :2], axis=2)  # Combine player channels
    
    print("\nBoard state:")
    for row in board_2d:
        print("  " + " ".join(str(int(cell)) for cell in row))
    
    # Show what moves were made from this board state
    print(f"\nMoves made from this board state:")
    moves_from_board = [moves[i] for i in indices]
    move_dist = Counter(moves_from_board)
    
    for col in range(7):
        count = move_dist.get(col, 0)
        percentage = (count / len(moves_from_board)) * 100
        print(f"  Column {col}: {count} times ({percentage:.1f}%)")
    
    # Check surrounding context
    print(f"\nContext around first occurrence (index {indices[0]}):")
    start_idx = max(0, indices[0] - 3)
    end_idx = min(len(X_sample), indices[0] + 4)
    
    for i in range(start_idx, end_idx):
        board = X_sample[i]
        move = moves[i]
        pieces = int(np.sum(board[:, :, 0]) + np.sum(board[:, :, 1]))
        marker = " <-- REPEATED BOARD" if i == indices[0] else ""
        print(f"\n  Index {i}:")
        print(f"    Pieces: {pieces}, Move: Column {move}{marker}")
        board_2d = np.sum(board[:, :, :2], axis=2)
        for row in board_2d:
            print(f"    {' '.join(str(int(cell)) for cell in row)}")
    
    # Check if this is an early-game state (common opening)
    pieces = int(np.sum(board_array[:, :, 0]) + np.sum(board_array[:, :, 1]))
    print(f"\nAnalysis:")
    print(f"  Pieces on board: {pieces}")
    if pieces <= 3:
        print(f"  ⚠️  This is an early-game state - common openings are expected")
        print(f"  This is likely normal - many games start similarly")
    else:
        print(f"  ⚠️  This is a mid/late-game state - unusual to repeat so often")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Investigate repeated board states')
    parser.add_argument('--data', type=str, default='training_data/processed/training_data.npz',
                       help='Path to training data file')
    parser.add_argument('--samples', type=int, default=30000,
                       help='Number of samples to analyze')
    
    args = parser.parse_args()
    
    investigate_repeated_board(args.data, args.samples)

