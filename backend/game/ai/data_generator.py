"""
Data generation for training neural network via self-play.
"""

import random
from typing import List, Tuple, Dict, Optional, Callable
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from ..board import Board
from ..game_engine import GameEngine
from ..win_checker import WinChecker
from .basic_ai import BasicAI


class TrainingExample:
    """Single training example."""
    def __init__(self, board_state: List[List[int]], move: int, current_player: int, 
                 outcome: str = None, move_number: int = None):
        self.board_state = board_state
        self.move = move
        self.current_player = current_player
        self.outcome = outcome  # 'win', 'loss', 'draw', or None
        self.move_number = move_number


def play_minimax_game(player1_depth: int = 4, player2_depth: int = 4, 
                     random_first_move: bool = False,
                     add_noise: bool = True) -> Tuple[List[TrainingExample], str, int]:
    """
    Play a single game between two minimax AIs and extract training examples.
    
    Args:
        player1_depth: Search depth for player 1 AI
        player2_depth: Search depth for player 2 AI
        random_first_move: If True, first move is random (for diversity)
    
    Returns:
        Tuple of (training_examples, result, winner)
        result: 'player1_won', 'player2_won', or 'draw'
        winner: 1, 2, or None
    """
    engine = GameEngine()
    ai1 = BasicAI(depth=player1_depth)
    ai1.set_player(Board.PLAYER1)
    ai2 = BasicAI(depth=player2_depth)
    ai2.set_player(Board.PLAYER2)
    
    examples = []
    move_number = 0
    
    # Random first move for diversity (increased probability)
    if random_first_move and random.random() < 0.5:
        valid_moves = engine.board.get_valid_moves()
        if valid_moves:
            first_move = random.choice(valid_moves)
            result = engine.make_move(first_move)
            if result['success']:
                move_number += 1
                examples.append(TrainingExample(
                    board_state=engine.board.get_board(),
                    move=first_move,
                    current_player=Board.PLAYER1,
                    move_number=move_number
                ))
    
    # Play game
    while engine.status == GameEngine.PLAYING:
        current_player = engine.current_player
        current_ai = ai1 if current_player == Board.PLAYER1 else ai2
        
        # Get board state before move
        board_before = [row[:] for row in engine.board.get_board()]
        
        # Get AI move
        move = current_ai.get_move(engine.board, current_player)
        
        # Make move
        result = engine.make_move(move)
        
        if result['success']:
            move_number += 1
            # Determine outcome (will be set after game ends)
            examples.append(TrainingExample(
                board_state=board_before,
                move=move,
                current_player=current_player,
                move_number=move_number
            ))
        else:
            # If move failed, try random valid move
            valid_moves = engine.board.get_valid_moves()
            if valid_moves:
                move = random.choice(valid_moves)
                result = engine.make_move(move)
                if result['success']:
                    move_number += 1
                    examples.append(TrainingExample(
                        board_state=board_before,
                        move=move,
                        current_player=current_player,
                        move_number=move_number
                    ))
    
    # Set outcomes for all examples
    if engine.status == GameEngine.WON:
        winner = engine.winner
        result_str = f'player{winner}_won'
        
        # Label examples: winning player's moves get 'win', losing player's get 'loss'
        for example in examples:
            if example.current_player == winner:
                example.outcome = 'win'
            else:
                example.outcome = 'loss'
    else:
        # Draw
        result_str = 'draw'
        winner = None
        for example in examples:
            example.outcome = 'draw'
    
    return examples, result_str, winner


def generate_games(num_games: int, player1_depth: int = 4, player2_depth: int = 4,
                  random_first_move: bool = True, progress_callback=None,
                  num_threads: int = 1, vary_depths: bool = True) -> List[TrainingExample]:
    """
    Generate multiple games via self-play and extract training examples.
    
    Args:
        num_games: Number of games to generate
        player1_depth: Search depth for player 1 AI
        player2_depth: Search depth for player 2 AI
        random_first_move: If True, sometimes use random first move
        progress_callback: Optional callback function(game_number, total_games)
        num_threads: Number of parallel threads (default: 1)
    
    Returns:
        List of all training examples from all games
    """
    if num_threads == 1:
        # Sequential generation
        all_examples = []
        
        for game_num in range(num_games):
            # Vary depths for more diversity
            p1_depth = player1_depth
            p2_depth = player2_depth
            if vary_depths:
                # Randomly vary depths by ±1 for variety
                import random
                p1_depth = max(2, player1_depth + random.randint(-1, 1))
                p2_depth = max(2, player2_depth + random.randint(-1, 1))
            
            examples, result, winner = play_minimax_game(
                player1_depth=p1_depth,
                player2_depth=p2_depth,
                random_first_move=random_first_move,
                add_noise=True
            )
            all_examples.extend(examples)
            
            if progress_callback:
                progress_callback(game_num + 1, num_games)
            
            # Print progress every 100 games
            if (game_num + 1) % 100 == 0:
                print(f"Generated {game_num + 1}/{num_games} games ({len(all_examples)} examples)")
        
        print(f"Generated {num_games} games with {len(all_examples)} total examples")
        return all_examples
    else:
        # Parallel generation using multiprocessing (needed for CPU-bound tasks due to GIL)
        all_examples = []
        completed_games = 0
        
        def generate_single_game(args_tuple):
            """Generate a single game (for parallel execution).
            
            Args:
                args_tuple: Tuple of (game_index, player1_depth, player2_depth, random_first_move, vary_depths)
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
        
        # Prepare arguments for each game (with depth variation flag)
        game_args = [
            (i, player1_depth, player2_depth, random_first_move, vary_depths)
            for i in range(num_games)
        ]
        
        with ProcessPoolExecutor(max_workers=num_threads) as executor:
            # Submit all games
            futures = {executor.submit(generate_single_game, args): args[0] for args in game_args}
            
            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    examples, game_index = future.result()
                    all_examples.extend(examples)
                    completed_games += 1
                    
                    if progress_callback:
                        progress_callback(completed_games, num_games)
                    
                    # Print progress every 100 games
                    if completed_games % 100 == 0:
                        print(f"Generated {completed_games}/{num_games} games ({len(all_examples)} examples)")
                except Exception as e:
                    print(f"Error generating game {futures[future]}: {e}")
        
        print(f"Generated {num_games} games with {len(all_examples)} total examples")
        return all_examples


def extract_training_data(examples: List[TrainingExample], include_outcome: bool = False) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract training data from examples.
    
    Args:
        examples: List of TrainingExample objects
        include_outcome: If True, include outcome labels (for future RL)
    
    Returns:
        Tuple of (X, y) where:
        - X: Board states as numpy array (n_examples, 6, 7, 2)
        - y: Move labels as one-hot encoded (n_examples, 7)
    """
    from .preprocessing import board_to_input
    
    X = []
    y = []
    
    for example in examples:
        # Convert board to input format
        board_input = board_to_input(example.board_state, example.current_player)
        X.append(board_input)
        
        # One-hot encode move
        move_onehot = np.zeros(7, dtype=np.float32)
        move_onehot[example.move] = 1.0
        y.append(move_onehot)
    
    return np.array(X), np.array(y)


def save_training_data(X: np.ndarray, y: np.ndarray, filepath: str):
    """
    Save training data to numpy file.
    
    Args:
        X: Input features
        y: Labels
        filepath: Path to save .npz file
    """
    np.savez(filepath, X=X, y=y)
    print(f"Saved training data to {filepath}")


def load_training_data(filepath: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load training data from numpy file.
    
    Args:
        filepath: Path to .npz file
    
    Returns:
        Tuple of (X, y)
    """
    data = np.load(filepath)
    return data['X'], data['y']

