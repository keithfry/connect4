# Neural Network AI for Connect 4

This directory contains the neural network-based AI system for Connect 4.

## Overview

The neural network AI uses a Convolutional Neural Network (CNN) to predict the best move given a board state. It is trained through self-play between minimax AI instances, then iteratively improved.

## Architecture

- **Input**: 6x7x2 board representation (one channel per player)
- **Output**: 7-class classification (one probability per column)
- **Model**: CNN with Conv2D layers, pooling, and dense layers

## Setup

1. Install dependencies:
```bash
uv pip install tensorflow numpy scikit-learn
```

Note: For Python 3.13, use regular `tensorflow` (not `tensorflow-macos`). TensorFlow 2.15+ supports Apple Silicon natively.

2. Verify GPU availability (on Apple Silicon):
```python
from backend.game.ai.gpu_config import check_gpu_availability
check_gpu_availability()
```

## Training

### Step 1: Generate Training Data

Generate games via self-play:
```bash
python scripts/generate_training_data.py --games 10000 --output training_data/processed/training_data.npz
```

Options:
- `--games`: Number of games to generate (default: 1000)
- `--player1-depth`: Minimax depth for player 1 (default: 4)
- `--player2-depth`: Minimax depth for player 2 (default: 4)
- `--output`: Output file path

### Step 2: Train Model

Train the neural network:
```bash
python scripts/train_model.py --data training_data/processed/training_data.npz --epochs 50 --batch-size 32
```

Options:
- `--data`: Path to training data .npz file
- `--epochs`: Number of training epochs (default: 50)
- `--batch-size`: Batch size (default: 32)
- `--model-version`: Model version identifier (default: v1)
- `--iterations`: Number of self-play iterations (default: 1)

If data file doesn't exist, you can generate it on the fly:
```bash
python scripts/train_model.py --games 10000 --epochs 50
```

## Usage

The neural network AI is automatically used in the API when available. It falls back to minimax if the model file is not found.

To use in code:
```python
from backend.game.ai.neural_ai import NeuralAI
from backend.game.board import Board

ai = NeuralAI(model_version="v1")
ai.set_player(2)  # AI is player 2
board = Board()
move = ai.get_move(board, current_player=2)
```

## Evaluation

Evaluate the model:
```python
from backend.game.ai.evaluator import evaluate_vs_minimax, evaluate_vs_random
from backend.game.ai.neural_ai import NeuralAI

ai = NeuralAI(model_version="v1")

# Evaluate vs minimax
results = evaluate_vs_minimax(ai, num_games=100, minimax_depth=4)
print(f"Win rate vs minimax: {results['win_rate']:.2%}")

# Evaluate vs random
results = evaluate_vs_random(ai, num_games=100)
print(f"Win rate vs random: {results['win_rate']:.2%}")
```

## Files

- `model.py`: CNN model architecture
- `preprocessing.py`: Board state preprocessing utilities
- `data_generator.py`: Self-play data generation
- `trainer.py`: Training pipeline
- `neural_ai.py`: Neural network AI implementation
- `evaluator.py`: Model evaluation utilities
- `gpu_config.py`: GPU configuration for Mac

## Model Storage

Trained models are saved in `backend/game/ai/models/`:
- `cnn_v1.h5`: Model weights
- `cnn_v1_config.json`: Model architecture
- `cnn_v1_history.json`: Training history

## Future Enhancements

- Policy + Value network (AlphaZero-style)
- Monte Carlo Tree Search (MCTS) integration
- Self-play reinforcement learning
- Model ensembling

