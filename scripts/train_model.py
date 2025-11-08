#!/usr/bin/env python
"""
Train Connect 4 neural network model.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import numpy as np
from backend.game.ai.trainer import ModelTrainer
from backend.game.ai.data_generator import load_training_data, generate_games, extract_training_data


def main():
    parser = argparse.ArgumentParser(description='Train Connect 4 neural network')
    parser.add_argument('--data', type=str, default='training_data/processed/training_data.npz',
                       help='Path to training data .npz file')
    parser.add_argument('--games', type=int, default=0,
                       help='Generate this many games if data file does not exist (default: 0)')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs (default: 50)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size (default: 32)')
    parser.add_argument('--validation-split', type=float, default=0.2,
                       help='Validation split ratio (default: 0.2)')
    parser.add_argument('--model-version', type=str, default='v1',
                       help='Model version identifier (default: v1)')
    parser.add_argument('--iterations', type=int, default=1,
                       help='Number of self-play iterations (default: 1)')
    
    args = parser.parse_args()
    
    # Load or generate training data
    data_path = Path(args.data)
    
    if data_path.exists():
        print(f"Loading training data from {data_path}")
        X, y = load_training_data(str(data_path))
    elif args.games > 0:
        print(f"Generating {args.games} games for training...")
        examples = generate_games(num_games=args.games, random_first_move=True)
        X, y = extract_training_data(examples)
        
        # Save generated data
        data_path.parent.mkdir(parents=True, exist_ok=True)
        from backend.game.ai.data_generator import save_training_data
        save_training_data(X, y, str(data_path))
    else:
        print(f"Error: Data file {data_path} not found and --games not specified")
        return
    
    print(f"Training data: X shape={X.shape}, y shape={y.shape}")
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    # Iterative training
    for iteration in range(args.iterations):
        print(f"\n{'='*60}")
        print(f"Iteration {iteration + 1}/{args.iterations}")
        print(f"{'='*60}")
        
        # Create or load model
        if iteration == 0:
            trainer.create_model(input_channels=X.shape[-1])
        else:
            # Load previous iteration's model
            trainer.load_model(version=args.model_version, input_channels=X.shape[-1])
        
        # Prepare data
        X_train, X_val, y_train, y_val = trainer.prepare_data(
            X, y, validation_split=args.validation_split
        )
        
        # Train
        history = trainer.train(
            X_train, y_train, X_val, y_val,
            epochs=args.epochs,
            batch_size=args.batch_size,
            model_version=args.model_version
        )
        
        # Evaluate
        train_metrics = trainer.evaluate(X_train, y_train)
        val_metrics = trainer.evaluate(X_val, y_val)
        
        print(f"\nTraining metrics: {train_metrics}")
        print(f"Validation metrics: {val_metrics}")
        
        # For future iterations, could generate more games using the trained model
        # This would be iterative self-play improvement
    
    print(f"\n{'='*60}")
    print("Training complete!")
    print(f"Model saved to: backend/game/ai/models/cnn_{args.model_version}.h5")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

