"""
API views for Connect 4 game.
"""

from datetime import datetime
from typing import Dict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .game_session import GameSession
from .board import Board
from .serializers import NewGameRequest, MoveRequest, GameStateResponse, ErrorResponse
from .ai.basic_ai import BasicAI
from .ai.neural_ai import NeuralAI


# In-memory storage for game sessions
_game_sessions: Dict[str, GameSession] = {}


@api_view(['GET'])
def health_check(request):
    """Health check endpoint for server startup verification."""
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def new_game(request):
    """Create a new game session."""
    try:
        data = NewGameRequest(**request.data)
        game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        session = GameSession(
            game_id=game_id,
            has_ai=data.has_ai,
            ai_player=data.ai_player
        )
        
        _game_sessions[game_id] = session
        
        state = session.get_state()
        response = GameStateResponse(**state)
        return Response(response.model_dump(), status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def make_move(request, game_id: str):
    """Make a move in the game."""
    try:
        if game_id not in _game_sessions:
            return Response(
                {'error': 'Game not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        session = _game_sessions[game_id]
        data = MoveRequest(**request.data)
        
        result = session.make_move(data.column)
        
        if not result['success']:
            # Get full state including game_id for error response
            full_state = session.get_state()
            error_response = ErrorResponse(
                error=result.get('error', 'Move failed'),
                state=GameStateResponse(**full_state)
            )
            return Response(
                error_response.model_dump(),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get full state including game_id
        full_state = session.get_state()
        response = GameStateResponse(**full_state)
        return Response(response.model_dump(), status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def get_state(request, game_id: str):
    """Get current game state."""
    try:
        if game_id not in _game_sessions:
            return Response(
                {'error': 'Game not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        session = _game_sessions[game_id]
        state = session.get_state()
        response = GameStateResponse(**state)
        return Response(response.model_dump(), status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def ai_move(request, game_id: str):
    """Request an AI move."""
    try:
        if game_id not in _game_sessions:
            return Response(
                {'error': 'Game not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        session = _game_sessions[game_id]
        
        if not session.has_ai:
            return Response(
                {'error': 'This game does not have an AI player'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not session.is_ai_turn():
            return Response(
                {'error': 'It is not the AI\'s turn'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get AI move - use neural AI (trained model)
        import logging
        logger = logging.getLogger(__name__)
        
        # Try to load neural AI
        ai = None
        try:
            ai = NeuralAI(model_version="v1")
            # Verify model actually loaded (not just fallback)
            if ai.model is not None and ai.masked_model is not None:
                # Check if it's a trained model by checking if weights are non-zero
                # (simple heuristic - if model exists, assume it's trained)
                model_file = ai.model_path / f"cnn_{ai.model_version}_best.h5"
                if not model_file.exists():
                    model_file = ai.model_path / f"cnn_{ai.model_version}.h5"
                
                if model_file.exists():
                    # Print to console for visibility
                    print(f"✓ Using Neural AI (model v1) for player {session.ai_player}")
                    print(f"  Model file: {model_file}")
                    print(f"  Model input shape: {ai.model.input_shape}")
                    logger.info(f"✓ Using Neural AI (model v1) for player {session.ai_player}")
                    logger.info(f"  Model file: {model_file}")
                    logger.info(f"  Model input shape: {ai.model.input_shape}")
                else:
                    logger.warning("Neural AI model file not found, falling back to minimax")
                    ai = None
            else:
                logger.warning("Neural AI model not initialized, falling back to minimax")
                ai = None
        except Exception as e:
            # Fallback to minimax if neural AI fails to load
            logger.warning(f"Failed to load Neural AI, falling back to minimax: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            ai = None
        
        # Fallback to minimax if neural AI not available
        if ai is None:
            ai = BasicAI(depth=4)
            logger.info(f"Using Minimax AI (depth 4) for player {session.ai_player}")
        
        ai.set_player(session.ai_player)
        board = Board(session.engine.board.get_board())
        ai_column = ai.get_move(board, session.engine.current_player)
        logger.debug(f"AI (player {session.ai_player}) chose column {ai_column}")
        
        # Make the move
        result = session.make_move(ai_column)
        
        if not result['success']:
            # Get full state including game_id for error response
            full_state = session.get_state()
            error_response = ErrorResponse(
                error=result.get('error', 'AI move failed'),
                state=GameStateResponse(**full_state)
            )
            return Response(
                error_response.model_dump(),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get full state including game_id
        full_state = session.get_state()
        response = GameStateResponse(**full_state)
        return Response(response.model_dump(), status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def reset_game(request, game_id: str):
    """Reset a game."""
    try:
        if game_id not in _game_sessions:
            return Response(
                {'error': 'Game not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        session = _game_sessions[game_id]
        session.reset()
        
        state = session.get_state()
        response = GameStateResponse(**state)
        return Response(response.model_dump(), status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
