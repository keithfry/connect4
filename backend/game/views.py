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


# In-memory storage for game sessions
_game_sessions: Dict[str, GameSession] = {}


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
        
        # Get AI move
        ai = BasicAI(depth=4)
        ai.set_player(session.ai_player)
        board = Board(session.engine.board.get_board())
        ai_column = ai.get_move(board, session.engine.current_player)
        
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
