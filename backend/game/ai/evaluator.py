"""
Evaluation utilities for neural network AI.
"""

import random
from typing import Dict, List
from ..board import Board
from ..game_engine import GameEngine
from ..win_checker import WinChecker
from .basic_ai import BasicAI
from .neural_ai import NeuralAI


def play_game(player1_strategy, player2_strategy, player1_name: str = "Player1", 
              player2_name: str = "Player2") -> Dict:
    """
    Play a single game between two strategies.
    
    Args:
        player1_strategy: Strategy for player 1 (must have get_move method)
        player2_strategy: Strategy for player 2 (must have get_move method)
        player1_name: Name for player 1
        player2_name: Name for player 2
    
    Returns:
        Dictionary with game result
    """
    engine = GameEngine()
    player1_strategy.set_player(Board.PLAYER1)
    player2_strategy.set_player(Board.PLAYER2)
    
    move_count = 0
    max_moves = 42  # Maximum possible moves
    
    while engine.status == GameEngine.PLAYING and move_count < max_moves:
        current_player = engine.current_player
        strategy = player1_strategy if current_player == Board.PLAYER1 else player2_strategy
        
        move = strategy.get_move(engine.board, current_player)
        result = engine.make_move(move)
        
        if result['success']:
            move_count += 1
        else:
            # If move failed, try random valid move
            valid_moves = engine.board.get_valid_moves()
            if valid_moves:
                move = random.choice(valid_moves)
                engine.make_move(move)
                move_count += 1
            else:
                break
    
    return {
        'status': engine.status,
        'winner': engine.winner,
        'moves': move_count,
        'result': 'player1_won' if engine.winner == 1 else 'player2_won' if engine.winner == 2 else 'draw'
    }


def evaluate_vs_minimax(neural_ai: NeuralAI, num_games: int = 100, 
                       minimax_depth: int = 4, neural_as_player: int = 1) -> Dict:
    """
    Evaluate neural network AI against minimax AI.
    
    Args:
        neural_ai: NeuralAI instance
        num_games: Number of games to play
        minimax_depth: Depth for minimax AI
        neural_as_player: Which player the neural AI should be (1 or 2)
    
    Returns:
        Dictionary with evaluation results
    """
    wins = 0
    losses = 0
    draws = 0
    
    for game_num in range(num_games):
        minimax_ai = BasicAI(depth=minimax_depth)
        
        if neural_as_player == 1:
            result = play_game(neural_ai, minimax_ai, "Neural", "Minimax")
            if result['winner'] == 1:
                wins += 1
            elif result['winner'] == 2:
                losses += 1
            else:
                draws += 1
        else:
            result = play_game(minimax_ai, neural_ai, "Minimax", "Neural")
            if result['winner'] == 2:
                wins += 1
            elif result['winner'] == 1:
                losses += 1
            else:
                draws += 1
        
        if (game_num + 1) % 10 == 0:
            print(f"Played {game_num + 1}/{num_games} games...")
    
    win_rate = wins / num_games if num_games > 0 else 0
    
    return {
        'total_games': num_games,
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'win_rate': win_rate
    }


def evaluate_vs_random(neural_ai: NeuralAI, num_games: int = 100, 
                      neural_as_player: int = 1) -> Dict:
    """
    Evaluate neural network AI against random moves.
    
    Args:
        neural_ai: NeuralAI instance
        num_games: Number of games to play
        neural_as_player: Which player the neural AI should be (1 or 2)
    
    Returns:
        Dictionary with evaluation results
    """
    class RandomStrategy:
        def __init__(self):
            self.player = None
        
        def set_player(self, player: int):
            self.player = player
        
        def get_move(self, board: Board, current_player: int) -> int:
            valid_moves = board.get_valid_moves()
            if valid_moves:
                return random.choice(valid_moves)
            return 0
    
    random_strategy = RandomStrategy()
    
    wins = 0
    losses = 0
    draws = 0
    
    for game_num in range(num_games):
        if neural_as_player == 1:
            result = play_game(neural_ai, random_strategy, "Neural", "Random")
            if result['winner'] == 1:
                wins += 1
            elif result['winner'] == 2:
                losses += 1
            else:
                draws += 1
        else:
            result = play_game(random_strategy, neural_ai, "Random", "Neural")
            if result['winner'] == 2:
                wins += 1
            elif result['winner'] == 1:
                losses += 1
            else:
                draws += 1
    
    win_rate = wins / num_games if num_games > 0 else 0
    
    return {
        'total_games': num_games,
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'win_rate': win_rate
    }


def analyze_move_quality(neural_ai: NeuralAI, num_positions: int = 100) -> Dict:
    """
    Analyze move quality by comparing neural network moves to minimax moves.
    
    Args:
        neural_ai: NeuralAI instance
        num_positions: Number of random positions to analyze
    
    Returns:
        Dictionary with analysis results
    """
    minimax_ai = BasicAI(depth=4)
    matches = 0
    top3_matches = 0
    
    for _ in range(num_positions):
        # Create random board position
        engine = GameEngine()
        # Make some random moves to create a position
        for _ in range(random.randint(5, 20)):
            valid_moves = engine.board.get_valid_moves()
            if not valid_moves or engine.status != GameEngine.PLAYING:
                break
            move = random.choice(valid_moves)
            engine.make_move(move)
            if engine.status != GameEngine.PLAYING:
                break
        
        if engine.status != GameEngine.PLAYING:
            continue
        
        current_player = engine.current_player
        
        # Get neural network move
        neural_move = neural_ai.get_move(engine.board, current_player)
        
        # Get minimax move
        minimax_move = minimax_ai.get_move(engine.board, current_player)
        
        if neural_move == minimax_move:
            matches += 1
        
        # Check if neural move is in top 3 minimax moves (simplified)
        # This would require getting top moves from minimax, which is more complex
        # For now, just count exact matches
    
    match_rate = matches / num_positions if num_positions > 0 else 0
    
    return {
        'total_positions': num_positions,
        'exact_matches': matches,
        'match_rate': match_rate
    }

