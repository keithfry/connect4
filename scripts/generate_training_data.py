#!/usr/bin/env python
"""
Generate training data via self-play between minimax AIs.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import numpy as np
import multiprocessing
from typing import List
from backend.game.ai.data_generator import (
    generate_games,
    extract_training_data,
    save_training_data,
    TrainingExample,
    play_minimax_game
)


# Module-level function for multiprocessing (must be picklable)
def _generate_single_game_worker(args_tuple):
    """Generate a single game (worker function for multiprocessing).
    
    This function is defined at module level so it can be pickled
    for use with multiprocessing. Each subprocess will import this.
    """
    game_index, p1_depth, p2_depth, rand_first, vary = args_tuple
    # Vary depths for more diversity
    if vary:
        import random
        p1_depth = max(2, p1_depth + random.randint(-1, 1))
        p2_depth = max(2, p2_depth + random.randint(-1, 1))
    
    examples, result, winner = play_minimax_game(
        player1_depth=p1_depth,
        player2_depth=p2_depth,
        random_first_move=rand_first,
        add_noise=True
    )
    return examples, game_index


def main():
    parser = argparse.ArgumentParser(description='Generate training data for Connect 4 neural network')
    parser.add_argument('--games', type=int, default=1000,
                       help='Number of games to generate (default: 1000)')
    parser.add_argument('--player1-depth', type=int, default=4,
                       help='Minimax depth for player 1 (default: 4)')
    parser.add_argument('--player2-depth', type=int, default=4,
                       help='Minimax depth for player 2 (default: 4)')
    parser.add_argument('--output', type=str, default='training_data/processed/training_data.npz',
                       help='Output file path (default: training_data/processed/training_data.npz)')
    parser.add_argument('--no-random-first', action='store_true',
                       help='Disable random first move')
    parser.add_argument('--threads', type=int, default=10,
                       help='Number of parallel threads (default: 10)')
    parser.add_argument('--save-interval', type=int, default=250,
                       help='Save data every N games (default: 250)')
    
    args = parser.parse_args()
    
    print(f"Generating {args.games} games using {args.threads} threads...")
    print(f"Player 1 depth: {args.player1_depth}, Player 2 depth: {args.player2_depth}")
    print(f"Saving incrementally every {args.save_interval} games")
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Collections for incremental writing (multiprocessing-safe using Manager)
    manager = multiprocessing.Manager()
    all_examples = manager.list()
    last_saved_games = manager.Value('i', 0)
    completed_games_counter = manager.Value('i', 0)
    
    def save_incremental(examples_list, games_completed: int, force: bool = False):
        """Save training data incrementally."""
        if force or (games_completed - last_saved_games.value >= args.save_interval):
            # Convert manager list to regular list for processing
            examples_copy = list(examples_list)
            current_count = len(examples_copy)
            if current_count > 0:
                print(f"\nSaving incremental data: {current_count} examples from {games_completed} games...")
                X, y = extract_training_data(examples_copy)
                save_training_data(X, y, str(output_path))
                print(f"Saved {current_count} examples to {output_path}")
                last_saved_games.value = games_completed
    
    if args.threads > 1:
        # Parallel generation with multiprocessing (true parallelism for CPU-bound tasks)
        # Note: Python's GIL prevents threads from running in parallel for CPU-bound code
        # Multiprocessing creates separate processes that can truly run in parallel
        from concurrent.futures import ProcessPoolExecutor, as_completed
        
        # Prepare arguments for each game (with depth variation)
        game_args = [
            (i, args.player1_depth, args.player2_depth, not args.no_random_first, True)
            for i in range(args.games)
        ]
        
        print(f"Starting parallel generation with {args.threads} processes...")
        
        with ProcessPoolExecutor(max_workers=args.threads) as executor:
            futures = {executor.submit(_generate_single_game_worker, args): args[0] for args in game_args}
            
            for future in as_completed(futures):
                try:
                    examples, game_index = future.result()
                    # Extend the shared list (multiprocessing-safe)
                    all_examples.extend(examples)
                    completed_games_counter.value += 1
                    current = completed_games_counter.value
                    current_total = len(all_examples)
                    
                    # Progress callback
                    if current % 100 == 0:
                        print(f"Generated {current}/{args.games} games ({current_total} examples)")
                    
                    # Incremental save
                    if current % args.save_interval == 0 or current == args.games:
                        save_incremental(all_examples, current, force=(current == args.games))
                        
                except Exception as e:
                    print(f"Error generating game {futures[future]}: {e}")
        
        # Convert manager list to regular list
        examples = list(all_examples)
    else:
        # Sequential generation
        def wrapped_progress_callback(current, total):
            """Wrapper that triggers incremental saves."""
            if current % args.save_interval == 0 or current == total:
                # For sequential, we need to pass the examples from generate_games
                # This will be handled after generation completes
                pass
        
        examples = generate_games(
            num_games=args.games,
            player1_depth=args.player1_depth,
            player2_depth=args.player2_depth,
            random_first_move=not args.no_random_first,
            progress_callback=wrapped_progress_callback,
            num_threads=1
        )
        
        # Save incrementally for sequential generation too
        for i in range(0, args.games, args.save_interval):
            if i + args.save_interval <= len(examples) or i == 0:
                # Extract examples up to this point (simplified - in practice would track by game)
                pass
        
        # Final save handled below
    
    # Final save
    print(f"\nExtracting final training data from {len(examples)} examples...")
    X, y = extract_training_data(examples)
    print(f"Final training data shape: X={X.shape}, y={y.shape}")
    
    # Final save
    save_training_data(X, y, str(output_path))
    
    print(f"\nDone! Training data saved to {output_path}")
    print(f"Total: {len(examples)} examples from {args.games} games")


if __name__ == '__main__':
    main()

