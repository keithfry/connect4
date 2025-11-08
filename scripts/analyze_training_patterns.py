#!/usr/bin/env python
"""
Analyze training data for pattern repetition and variety.
"""

import sys
from pathlib import Path
import numpy as np
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.game.ai.data_generator import load_training_data


def analyze_patterns(data_path, num_samples=30000):
    """Analyze training data for repeated patterns."""
    print(f"Loading training data from: {data_path}")
    
    try:
        X, y = load_training_data(data_path)
        print(f"Total examples in dataset: {len(X)}")
        
        # Analyze first N samples
        sample_size = min(num_samples, len(X))
        print(f"\nAnalyzing first {sample_size} examples...")
        
        X_sample = X[:sample_size]
        y_sample = y[:sample_size]
        moves = np.argmax(y_sample, axis=1)
        
        # 1. Check for unique board states
        print("\n" + "="*60)
        print("1. Board State Uniqueness")
        print("="*60)
        
        unique_boards = {}
        board_counts = Counter()
        
        for i, board in enumerate(X_sample):
            # Convert to hashable format
            board_tuple = tuple(board.flatten())
            board_counts[board_tuple] += 1
            
            if board_tuple not in unique_boards:
                unique_boards[board_tuple] = i
        
        print(f"Unique board states: {len(unique_boards)}")
        print(f"Total examples: {sample_size}")
        print(f"Uniqueness ratio: {len(unique_boards)/sample_size*100:.2f}%")
        
        # Check for highly repeated boards
        repeated_boards = [(board, count) for board, count in board_counts.items() if count > 10]
        if repeated_boards:
            print(f"\n⚠️  Found {len(repeated_boards)} board states repeated >10 times")
            print("Top 10 most repeated boards:")
            for board_tuple, count in sorted(repeated_boards, key=lambda x: x[1], reverse=True)[:10]:
                print(f"  Repeated {count} times (first seen at index {unique_boards[board_tuple]})")
        
        # 2. Check move sequences for patterns
        print("\n" + "="*60)
        print("2. Move Sequence Patterns")
        print("="*60)
        
        # Look for repeated move sequences
        sequence_length = 10
        sequences = []
        for i in range(len(moves) - sequence_length + 1):
            seq = tuple(moves[i:i+sequence_length])
            sequences.append(seq)
        
        sequence_counts = Counter(sequences)
        repeated_sequences = [(seq, count) for seq, count in sequence_counts.items() if count > 5]
        
        if repeated_sequences:
            print(f"⚠️  Found {len(repeated_sequences)} move sequences repeated >5 times")
            print("Top 10 most repeated sequences:")
            for seq, count in sorted(repeated_sequences, key=lambda x: x[1], reverse=True)[:10]:
                print(f"  Sequence {list(seq)}: repeated {count} times")
        else:
            print("✓ No highly repeated move sequences found")
        
        # 3. Check for sequential column filling pattern
        print("\n" + "="*60)
        print("3. Sequential Column Filling Pattern")
        print("="*60)
        
        # Check if moves follow pattern: fill column 0, then 1, then 2, etc.
        consecutive_same_col = 0
        max_consecutive = 0
        pattern_detected = False
        
        for i in range(1, min(1000, len(moves))):
            if moves[i] == moves[i-1]:
                consecutive_same_col += 1
                max_consecutive = max(max_consecutive, consecutive_same_col)
                if consecutive_same_col >= 5:
                    pattern_detected = True
            else:
                consecutive_same_col = 0
        
        print(f"Maximum consecutive same column: {max_consecutive}")
        if pattern_detected:
            print("⚠️  WARNING: Detected pattern of filling columns sequentially!")
        else:
            print("✓ No sequential column filling pattern detected")
        
        # 4. Analyze board state diversity by piece count
        print("\n" + "="*60)
        print("4. Board State Diversity by Game Stage")
        print("="*60)
        
        piece_counts = []
        for i in range(sample_size):
            board = X_sample[i]
            pieces = int(np.sum(board[:, :, 0]) + np.sum(board[:, :, 1]))
            piece_counts.append(pieces)
        
        piece_count_dist = Counter(piece_counts)
        print(f"Unique piece counts: {len(piece_count_dist)}")
        print(f"Piece count range: {min(piece_counts)} - {max(piece_counts)}")
        print(f"Average pieces per board: {np.mean(piece_counts):.2f}")
        
        # Check if piece counts are evenly distributed
        if len(piece_count_dist) < 20:
            print("⚠️  WARNING: Very few unique piece counts - might indicate repetitive games")
        
        # 5. Check move distribution
        print("\n" + "="*60)
        print("5. Move Distribution")
        print("="*60)
        
        move_dist = Counter(moves)
        print("Move distribution (columns 0-6):")
        for col in range(7):
            count = move_dist.get(col, 0)
            percentage = (count / sample_size) * 100
            print(f"  Column {col}: {count:6d} ({percentage:5.2f}%)")
        
        # Check if distribution is too skewed
        max_percentage = max(percentage for _, percentage in [(col, (move_dist.get(col, 0) / sample_size) * 100) for col in range(7)])
        if max_percentage > 30:
            print(f"⚠️  WARNING: One column ({max_percentage:.1f}%) dominates - might indicate bias")
        
        # 6. Check for game boundaries (piece count resets)
        print("\n" + "="*60)
        print("6. Game Boundaries")
        print("="*60)
        
        resets = []
        for i in range(1, len(piece_counts)):
            if piece_counts[i] < piece_counts[i-1]:
                resets.append(i)
        
        print(f"Found {len(resets)} game boundaries (piece count resets)")
        if len(resets) > 0:
            avg_game_length = sample_size / len(resets) if len(resets) > 0 else 0
            print(f"Average game length: {avg_game_length:.1f} moves")
            
            # Check if games are similar length
            game_lengths = []
            for i in range(len(resets)):
                start = resets[i-1] if i > 0 else 0
                end = resets[i]
                game_lengths.append(end - start)
            
            if len(game_lengths) > 1:
                print(f"Game length range: {min(game_lengths)} - {max(game_lengths)} moves")
                if max(game_lengths) - min(game_lengths) < 5:
                    print("⚠️  WARNING: Games are very similar length - might be repetitive")
        
        # 7. Sample some actual board states to visualize
        print("\n" + "="*60)
        print("7. Sample Board States")
        print("="*60)
        
        print("First 5 board states (showing piece positions):")
        for i in range(min(5, sample_size)):
            board = X_sample[i]
            move = moves[i]
            pieces = int(np.sum(board[:, :, 0]) + np.sum(board[:, :, 1]))
            print(f"\nExample {i+1}:")
            print(f"  Pieces on board: {pieces}")
            print(f"  Move made: Column {move}")
            # Show board state
            board_2d = np.sum(board[:, :, :2], axis=2)  # Combine player channels
            print("  Board:")
            for row in board_2d:
                print(f"    {' '.join(str(int(cell)) for cell in row)}")
        
        # 8. Overall assessment
        print("\n" + "="*60)
        print("8. Overall Assessment")
        print("="*60)
        
        issues = []
        if len(unique_boards) / sample_size < 0.1:
            issues.append("Low board state uniqueness (<10%)")
        if len(repeated_boards) > 100:
            issues.append(f"Many repeated boards ({len(repeated_boards)})")
        if pattern_detected:
            issues.append("Sequential column filling pattern detected")
        if max_percentage > 30:
            issues.append(f"Move distribution too skewed (max: {max_percentage:.1f}%)")
        
        if issues:
            print("⚠️  ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
            print("\nRecommendation: Regenerate training data with more variety")
        else:
            print("✓ Training data looks good - good variety and no obvious patterns")
        
    except Exception as e:
        print(f"Error analyzing training data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze training data for patterns')
    parser.add_argument('--data', type=str, default='training_data/processed/training_data.npz',
                       help='Path to training data file')
    parser.add_argument('--samples', type=int, default=30000,
                       help='Number of samples to analyze (default: 30000)')
    
    args = parser.parse_args()
    
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Error: Training data file not found: {data_path}")
        sys.exit(1)
    
    analyze_patterns(str(data_path), args.samples)

