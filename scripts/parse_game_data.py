#!/usr/bin/env python3
"""
Parse game data files from backend/game_data and convert to training examples.

This script reads JSON game recordings and converts them to TrainingExample format
that can be used to augment the neural network training data.
"""

import json
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path (not backend itself)
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import TrainingExample directly to avoid TensorFlow dependency
from typing import List as TypingList
from backend.game.board import Board

# Define TrainingExample locally to avoid importing data_generator (which imports tensorflow)
class TrainingExample:
    """Single training example."""
    def __init__(self, board_state: TypingList[TypingList[int]], move: int, current_player: int, 
                 outcome: str = None, move_number: int = None):
        self.board_state = board_state
        self.move = move
        self.current_player = current_player
        self.outcome = outcome  # 'win', 'loss', 'draw', or None
        self.move_number = move_number


def parse_game_file(file_path: Path) -> List[TrainingExample]:
    """
    Parse a single game JSON file and extract training examples.
    
    Args:
        file_path: Path to the game JSON file
        
    Returns:
        List of TrainingExample objects
    """
    try:
        with open(file_path, 'r') as f:
            game_data = json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
    
    moves = game_data.get('moves', [])
    if not moves:
        return []
    
    result = game_data.get('result', 'draw')
    winner = game_data.get('winner')
    
    examples = []
    
    # Use previous move's board_state as the "before" state for current move
    board_state_before = None
    
    for i, move_record in enumerate(moves):
        move_number = move_record.get('move_number', i + 1)
        player = move_record.get('player')
        column = move_record.get('column')
        board_state_after = move_record.get('board_state')
        
        if player is None or column is None or board_state_after is None:
            continue
        
        # For the first move, board_state_before is empty
        if board_state_before is None:
            board_state_before = [[0] * 7 for _ in range(6)]
        
        # Create training example with board state BEFORE the move
        example = TrainingExample(
            board_state=[row[:] for row in board_state_before],  # Deep copy
            move=column,
            current_player=player,
            move_number=move_number
        )
        
        # Determine outcome based on game result
        if result == 'draw':
            example.outcome = 'draw'
        elif winner:
            if player == winner:
                example.outcome = 'win'
            else:
                example.outcome = 'loss'
        else:
            # If result is not clear, try to infer from move position
            # (last moves of winning player are wins, etc.)
            example.outcome = None
        
        examples.append(example)
        
        # Use current move's board_state as the "before" state for next move
        board_state_before = board_state_after
    
    return examples


def parse_all_game_files(game_data_dir: str = "backend/game_data") -> List[TrainingExample]:
    """
    Parse all game JSON files in the game_data directory.
    
    Args:
        game_data_dir: Directory containing game JSON files
        
    Returns:
        List of all TrainingExample objects from all games
    """
    game_dir = Path(game_data_dir)
    if not game_dir.exists():
        print(f"Game data directory not found: {game_data_dir}")
        return []
    
    all_examples = []
    json_files = sorted(game_dir.glob("game_*.json"))
    
    print(f"Found {len(json_files)} game files in {game_data_dir}")
    
    for json_file in json_files:
        examples = parse_game_file(json_file)
        all_examples.extend(examples)
        if len(examples) > 0:
            print(f"  Parsed {json_file.name}: {len(examples)} moves")
    
    print(f"\nTotal: {len(all_examples)} training examples from {len(json_files)} games")
    return all_examples


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse game data files to training examples")
    parser.add_argument(
        "--game-data-dir",
        type=str,
        default="backend/game_data",
        help="Directory containing game JSON files (default: backend/game_data)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file to save training examples (optional, prints summary if not provided)"
    )
    
    args = parser.parse_args()
    
    # Parse all game files
    examples = parse_all_game_files(args.game_data_dir)
    
    if not examples:
        print("No training examples found.")
        return
    
    # Print statistics
    wins = sum(1 for e in examples if e.outcome == 'win')
    losses = sum(1 for e in examples if e.outcome == 'loss')
    draws = sum(1 for e in examples if e.outcome == 'draw')
    unknown = sum(1 for e in examples if e.outcome is None)
    
    print(f"\nOutcome distribution:")
    print(f"  Wins: {wins}")
    print(f"  Losses: {losses}")
    print(f"  Draws: {draws}")
    print(f"  Unknown: {unknown}")
    
    # Save to file if requested
    if args.output:
        from game.ai.data_generator import extract_training_data, save_training_data
        X, y = extract_training_data(examples)
        save_training_data(X, y, args.output)
        print(f"\nSaved training data to {args.output}")


if __name__ == "__main__":
    main()

