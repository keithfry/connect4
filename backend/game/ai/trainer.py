"""
Training pipeline for Connect 4 neural network.
"""

import os
import json
from pathlib import Path
from typing import Tuple, Dict, Optional
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split

from .model import create_cnn_model, MaskedMoveModel
from .gpu_config import configure_gpu, get_device_info
from .preprocessing import prepare_batch


class ModelTrainer:
    """Handles model training and evaluation."""
    
    def __init__(self, model_dir: str = "backend/game/ai/models"):
        """
        Initialize trainer.
        
        Args:
            model_dir: Directory to save/load models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.history = None
        
        # Configure GPU
        configure_gpu()
        device_info = get_device_info()
        print(f"Training device info: {device_info}")
    
    def create_model(self, input_channels: int = 2) -> keras.Model:
        """
        Create a new model.
        
        Args:
            input_channels: Number of input channels (2 or 3)
        
        Returns:
            Keras model
        """
        self.model = create_cnn_model(input_channels=input_channels)
        return self.model
    
    def prepare_data(self, X: np.ndarray, y: np.ndarray, 
                    validation_split: float = 0.2, random_state: int = 42) -> Tuple:
        """
        Prepare training and validation data.
        
        Args:
            X: Input features
            y: Labels
            validation_split: Fraction of data for validation
            random_state: Random seed
        
        Returns:
            Tuple of (X_train, X_val, y_train, y_val)
        """
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=random_state
        )
        
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        
        return X_train, X_val, y_train, y_val
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray,
              epochs: int = 50, batch_size: int = 32,
              model_version: str = "v1") -> Dict:
        """
        Train the model.
        
        Args:
            X_train: Training inputs
            y_train: Training labels
            X_val: Validation inputs
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size
            model_version: Model version identifier
        
        Returns:
            Training history dictionary
        """
        if self.model is None:
            # Determine input channels from data shape
            input_channels = X_train.shape[-1]
            self.create_model(input_channels=input_channels)
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ModelCheckpoint(
                filepath=str(self.model_dir / f"cnn_{model_version}_best.weights.h5"),
                monitor='val_loss',
                save_best_only=True,
                save_weights_only=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=1
            )
        ]
        
        # Train
        print(f"Training model for {epochs} epochs...")
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final model
        self.save_model(model_version)
        
        return self.history.history
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Evaluate model on data.
        
        Args:
            X: Input features
            y: Labels
        
        Returns:
            Dictionary of metrics
        """
        if self.model is None:
            raise ValueError("Model not loaded or created")
        
        results = self.model.evaluate(X, y, verbose=0)
        metrics = {
            'loss': results[0],
            'accuracy': results[1],
            'top_k_accuracy': results[2] if len(results) > 2 else None
        }
        
        return metrics
    
    def save_model(self, version: str = "v1"):
        """
        Save model and training history.
        
        Args:
            version: Model version identifier
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        # Save model weights
        model_path = self.model_dir / f"cnn_{version}.weights.h5"
        self.model.save_weights(str(model_path))
        print(f"Saved model weights to {model_path}")
        
        # Save model architecture
        config_path = self.model_dir / f"cnn_{version}_config.json"
        with open(config_path, 'w') as f:
            json.dump(self.model.to_json(), f, indent=2)
        
        # Save training history
        if self.history:
            history_path = self.model_dir / f"cnn_{version}_history.json"
            with open(history_path, 'w') as f:
                json.dump(self.history.history, f, indent=2)
    
    def load_model(self, version: str = "v1", input_channels: int = 2) -> keras.Model:
        """
        Load a saved model.
        
        Args:
            version: Model version identifier
            input_channels: Number of input channels (must match saved model)
        
        Returns:
            Loaded Keras model
        """
        # Create model architecture
        self.model = create_cnn_model(input_channels=input_channels)
        
        # Load weights - try both .weights.h5 and .h5 for backwards compatibility
        model_path = self.model_dir / f"cnn_{version}.weights.h5"
        if not model_path.exists():
            # Fallback to old format
            model_path = self.model_dir / f"cnn_{version}.h5"
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_dir / f'cnn_{version}.weights.h5'}")
        
        self.model.load_weights(str(model_path))
        print(f"Loaded model from {model_path}")
        
        return self.model
    
    def get_model(self) -> Optional[keras.Model]:
        """Get the current model."""
        return self.model

