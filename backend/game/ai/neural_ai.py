"""
Neural network-based AI implementation for Connect 4.
"""

import numpy as np
from typing import Optional
from ..board import Board
from .ai_strategy import AIStrategy
from .model import MaskedMoveModel, create_cnn_model
from .preprocessing import board_to_input
from tensorflow import keras
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class NeuralAI(AIStrategy):
    """Neural network-based AI player."""
    
    def __init__(self, model_version: str = "v1", model_path: Optional[str] = None):
        """
        Initialize neural network AI.
        
        Args:
            model_version: Version of model to load (e.g., "v1")
            model_path: Optional path to model directory (defaults to backend/game/ai/models)
        """
        self.model_version = model_version
        
        # Resolve model path - handle both relative and absolute paths
        if model_path:
            self.model_path = Path(model_path)
        else:
            # Try to find models directory relative to this file
            current_file = Path(__file__).resolve()
            # This file is in backend/game/ai/, so models/ is in the same directory
            self.model_path = current_file.parent / "models"
            # Fallback to relative path if absolute doesn't work
            if not self.model_path.exists():
                self.model_path = Path("backend/game/ai/models")
        
        self.model = None
        self.masked_model = None
        self.player = Board.PLAYER2  # Default to player 2
        
        self._load_model()
    
    def _load_model(self):
        """Load the trained model."""
        try:
            # Try to load model weights - check for best version first, then regular
            # New format: .weights.h5, old format: .h5 (for backwards compatibility)
            model_file_best_new = self.model_path / f"cnn_{self.model_version}_best.weights.h5"
            model_file_best_old = self.model_path / f"cnn_{self.model_version}_best.h5"
            model_file_regular_new = self.model_path / f"cnn_{self.model_version}.weights.h5"
            model_file_regular_old = self.model_path / f"cnn_{self.model_version}.h5"
            
            model_file = None
            if model_file_best_new.exists():
                model_file = model_file_best_new
            elif model_file_best_old.exists():
                model_file = model_file_best_old
            elif model_file_regular_new.exists():
                model_file = model_file_regular_new
            elif model_file_regular_old.exists():
                model_file = model_file_regular_old
            
            if model_file is None or not model_file.exists():
                logger.warning(f"Model file not found. Checked: {model_file_best_new}, {model_file_best_old}, {model_file_regular_new}, {model_file_regular_old}")
                logger.warning("Neural AI will use random initialization - moves will be random!")
                # Create untrained model as fallback with 3 channels to match input format
                self.model = create_cnn_model(input_channels=3)
                self.masked_model = MaskedMoveModel(self.model)
                return
            
            # Create model architecture - try 3 channels first (with current player), then 2
            # The model was likely trained with 3 channels (board + current player indicator)
            try:
                self.model = create_cnn_model(input_channels=3)
                self.model.load_weights(str(model_file))
                # Print to console for visibility (in addition to logging)
                print(f"✓ Neural AI: Loaded trained model from {model_file}")
                logger.info(f"✓ Loaded neural network model with 3 input channels: {model_file}")
            except (ValueError, Exception) as e:
                # Try with 2 channels if 3 doesn't work
                logger.debug(f"3-channel model failed, trying 2-channel: {e}")
                try:
                    self.model = create_cnn_model(input_channels=2)
                    self.model.load_weights(str(model_file))
                    logger.info(f"✓ Loaded neural network model with 2 input channels: {model_file}")
                except Exception as e2:
                    logger.error(f"Failed to load model with both 2 and 3 channels: {e2}")
                    raise
            
            self.masked_model = MaskedMoveModel(self.model)
            
        except Exception as e:
            logger.error(f"Error loading neural network model: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback to untrained model with 3 channels to match input format
            self.model = create_cnn_model(input_channels=3)
            self.masked_model = MaskedMoveModel(self.model)
            logger.warning("Neural AI initialized with untrained model due to error - moves will be random!")
    
    def set_player(self, player: int):
        """Set which player the AI is."""
        self.player = player
    
    def get_move(self, board: Board, current_player: int) -> int:
        """
        Get the best move using the neural network.
        
        Args:
            board: Current board state
            current_player: Current player (1 or 2)
        
        Returns:
            Column index for best move
        """
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0
        
        # CRITICAL: Check for immediate wins first (highest priority)
        from ..win_checker import WinChecker
        win_checker = WinChecker()
        
        for move in valid_moves:
            test_board = Board(board.get_board())
            test_board.place_piece(move, current_player)
            winner = win_checker.check_winner(test_board)
            if winner == current_player:
                logger.info(f"Neural AI: Found winning move in column {move}")
                return move
        
        # CRITICAL: Check for blocks (opponent about to win)
        opponent = Board.PLAYER1 if current_player == Board.PLAYER2 else Board.PLAYER2
        for move in valid_moves:
            test_board = Board(board.get_board())
            test_board.place_piece(move, opponent)
            winner = win_checker.check_winner(test_board)
            if winner == opponent:
                logger.info(f"Neural AI: Blocking opponent win in column {move}")
                return move
        
        # Use neural network for other moves
        if self.masked_model is None:
            # Fallback to random valid move
            return np.random.choice(valid_moves)
        
        try:
            # Convert board to input format
            # Use current_player to create 3-channel input (matches training)
            board_state = board.get_board()
            # Always include current_player to match training data format (3 channels)
            board_input = board_to_input(board_state, current_player)
            
            # Predict move
            predicted_column, probabilities = self.masked_model.predict(board_input, board)
            
            # Reduced exploration for more deterministic play
            # Only add small amount of randomness when model is uncertain
            max_prob = np.max(probabilities)
            temperature = 0.3 if max_prob < 0.3 else 0.1  # Lower temp when confident
            epsilon = 0.05  # Only 5% random exploration (reduced from 15%)
            
            # Epsilon-greedy: rarely explore randomly
            if np.random.random() < epsilon:
                predicted_column = np.random.choice(valid_moves)
            else:
                # Apply small temperature for slight variety
                log_probs = np.log(probabilities + 1e-10) / (1.0 + temperature)
                exp_probs = np.exp(log_probs - np.max(log_probs))  # Numerical stability
                exp_probs = exp_probs / np.sum(exp_probs)  # Renormalize
                
                # Sample from the temperature-adjusted distribution
                valid_probs = exp_probs[valid_moves]
                valid_probs = valid_probs / np.sum(valid_probs)  # Renormalize
                predicted_column = np.random.choice(valid_moves, p=valid_probs)
            
            # Verify it's a valid move
            if not board.is_column_full(predicted_column):
                return predicted_column
            
            # If predicted move is invalid, fallback to random valid move
            if valid_moves:
                logger.warning(f"Predicted invalid move {predicted_column}, using random valid move")
                return np.random.choice(valid_moves)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error in neural network prediction: {e}")
            # Fallback to random valid move
            valid_moves = board.get_valid_moves()
            if valid_moves:
                return np.random.choice(valid_moves)
            return 0

