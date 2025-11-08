#!/usr/bin/env python
"""
Inspect training data to check for variety and patterns.
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.game.ai.data_generator import load_training_data


def analyze_training_data(data_path):
    """Analyze training data for variety and patterns."""
    print(f"Loading training data from: {data_path}")
    
    try:
        X, y = load_training_data(data_path)
        print(f"\nData loaded successfully!")
        print(f"  Total examples: {len(X)}")
        print(f"  Input shape: {X.shape}")
        print(f"  Output shape: {y.shape}")
        
        # Analyze move distribution
        moves = np.argmax(y, axis=1)  # Get the column for each move
        print(f"\nMove Distribution (columns 0-6):")
        unique, counts = np.unique(moves, return_counts=True)
        for col, count in zip(unique, counts):
            percentage = (count / len(moves)) * 100
            print(f"  Column {col}: {count:6d} moves ({percentage:5.2f}%)")
        
        # Check for variety in board states
        print(f"\nBoard State Variety:")
        # Sample some board states and check if they're unique
        sample_size = min(1000, len(X))
        sample_indices = np.random.choice(len(X), sample_size, replace=False)
        sample_boards = X[sample_indices]
        
        # Check how many unique board states we have in the sample
        unique_boards = set()
        for board in sample_boards:
            # Convert to tuple for hashing
            board_tuple = tuple(board.flatten())
            unique_boards.add(board_tuple)
        
        print(f"  Sampled {sample_size} board states")
        print(f"  Unique board states in sample: {len(unique_boards)}")
        print(f"  Variety ratio: {len(unique_boards)/sample_size*100:.2f}%")
        
        # Check for patterns in move sequences
        print(f"\nMove Sequence Analysis:")
        # Look at first 100 moves to see if there's a pattern
        first_100_moves = moves[:100]
        print(f"  First 100 moves: {first_100_moves.tolist()}")
        
        # Check if moves alternate or follow a pattern
        consecutive_same = 0
        max_consecutive = 0
        current_consecutive = 1
        for i in range(1, len(moves)):
            if moves[i] == moves[i-1]:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
        
        print(f"  Maximum consecutive same column: {max_consecutive}")
        
        # Check board state diversity by counting non-zero cells
        print(f"\nBoard State Analysis:")
        non_zero_counts = []
        for i in range(min(100, len(X))):
            board = X[i]
            # Count pieces on board (channels 0 and 1)
            pieces = np.sum(board[:, :, 0]) + np.sum(board[:, :, 1])
            non_zero_counts.append(pieces)
        
        print(f"  Average pieces per board (first 100): {np.mean(non_zero_counts):.2f}")
        print(f"  Min pieces: {np.min(non_zero_counts)}, Max pieces: {np.max(non_zero_counts)}")
        
        # Check if all examples are from the same game (same number of pieces)
        if len(set(non_zero_counts)) < 10:
            print(f"  ⚠️  WARNING: Very little variation in piece counts - might be same game repeated!")
        
        # Check move distribution per game stage
        print(f"\nMove Distribution by Game Stage:")
        non_zero_counts_array = np.array(non_zero_counts)
        if len(non_zero_counts_array) > 0:
            early_game = moves[:len(non_zero_counts_array)][non_zero_counts_array < 10]
            mid_game = moves[:len(non_zero_counts_array)][(non_zero_counts_array >= 10) & (non_zero_counts_array < 30)]
            late_game = moves[:len(non_zero_counts_array)][non_zero_counts_array >= 30]
        else:
            early_game = []
            mid_game = []
            late_game = []
        
        if len(early_game) > 0:
            early_unique, early_counts = np.unique(early_game, return_counts=True)
            print(f"  Early game ({len(early_game)} moves):")
            for col, count in zip(early_unique, early_counts):
                print(f"    Column {col}: {count} ({count/len(early_game)*100:.1f}%)")
        
        if len(mid_game) > 0:
            mid_unique, mid_counts = np.unique(mid_game, return_counts=True)
            print(f"  Mid game ({len(mid_game)} moves):")
            for col, count in zip(mid_unique, mid_counts):
                print(f"    Column {col}: {count} ({count/len(mid_game)*100:.1f}%)")
        
        if len(late_game) > 0:
            late_unique, late_counts = np.unique(late_game, return_counts=True)
            print(f"  Late game ({len(late_game)} moves):")
            for col, count in zip(late_unique, late_counts):
                print(f"    Column {col}: {count} ({count/len(late_game)*100:.1f}%)")
        
    except Exception as e:
        print(f"Error loading training data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Inspect training data')
    parser.add_argument('--data', type=str, default='training_data/processed/training_data.npz',
                       help='Path to training data file')
    
    args = parser.parse_args()
    
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: Training data file not found: {data_path}")
        print("Generate training data first with:")
        print("  python scripts/generate_training_data.py --games 1000")
        sys.exit(1)
    
    analyze_training_data(str(data_path))

