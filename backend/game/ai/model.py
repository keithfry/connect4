"""
CNN model architecture for Connect 4 move prediction.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from typing import Tuple
from .preprocessing import apply_move_mask
from ..board import Board


def create_cnn_model(input_channels: int = 2) -> keras.Model:
    """
    Create CNN model for Connect 4 move prediction.
    
    Args:
        input_channels: Number of input channels (2 or 3)
    
    Returns:
        Compiled Keras model
    """
    # Input: (6, 7, input_channels)
    inputs = keras.Input(shape=(Board.ROWS, Board.COLS, input_channels), name='board_input')
    
    # Convolutional layers
    x = layers.Conv2D(32, kernel_size=3, activation='relu', padding='same', name='conv1')(inputs)
    x = layers.Conv2D(64, kernel_size=3, activation='relu', padding='same', name='conv2')(x)
    x = layers.Conv2D(64, kernel_size=3, activation='relu', padding='same', name='conv3')(x)
    
    # Global average pooling (reduces spatial dimensions)
    x = layers.GlobalAveragePooling2D(name='global_pool')(x)
    
    # Dense layers
    x = layers.Dense(128, activation='relu', name='dense1')(x)
    x = layers.Dropout(0.3, name='dropout1')(x)
    x = layers.Dense(64, activation='relu', name='dense2')(x)
    x = layers.Dropout(0.2, name='dropout2')(x)
    
    # Output: 7 classes (one per column)
    outputs = layers.Dense(7, activation='softmax', name='move_output')(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs, name='connect4_cnn')
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'top_k_categorical_accuracy']
    )
    
    return model


class MaskedMoveModel:
    """
    Wrapper around Keras model that applies move masking.
    """
    
    def __init__(self, model: keras.Model):
        """
        Initialize with a Keras model.
        
        Args:
            model: Compiled Keras model
        """
        self.model = model
    
    def predict(self, board_state: np.ndarray, board: Board) -> Tuple[int, np.ndarray]:
        """
        Predict move with masking applied.
        
        Args:
            board_state: Preprocessed board state (6, 7, channels)
            board: Board instance for move masking
        
        Returns:
            Tuple of (predicted_column, probabilities)
        """
        # Add batch dimension
        if len(board_state.shape) == 3:
            board_state = np.expand_dims(board_state, axis=0)
        
        # Get raw predictions
        raw_predictions = self.model.predict(board_state, verbose=0)[0]
        
        # Create move mask
        from .preprocessing import create_move_mask
        mask = create_move_mask(board)
        
        # Apply mask and renormalize
        masked_predictions = apply_move_mask(raw_predictions, mask)
        
        # Get best move
        predicted_column = int(np.argmax(masked_predictions))
        
        return predicted_column, masked_predictions
    
    def predict_batch(self, board_states: np.ndarray, boards: list) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict moves for a batch of board states.
        
        Args:
            board_states: Batch of preprocessed board states (batch_size, 6, 7, channels)
            boards: List of Board instances for move masking
        
        Returns:
            Tuple of (predicted_columns, probabilities)
        """
        # Get raw predictions
        raw_predictions = self.model.predict(board_states, verbose=0)
        
        # Apply masking for each board
        masked_predictions = []
        predicted_columns = []
        
        for i, board in enumerate(boards):
            from .preprocessing import create_move_mask
            mask = create_move_mask(board)
            masked = apply_move_mask(raw_predictions[i], mask)
            masked_predictions.append(masked)
            predicted_columns.append(int(np.argmax(masked)))
        
        return np.array(predicted_columns), np.array(masked_predictions)

