"""
Basic tests for game engine.
"""

from django.test import TestCase
from .board import Board
from .win_checker import WinChecker
from .game_engine import GameEngine


class BoardTestCase(TestCase):
    """Test board functionality."""
    
    def test_board_creation(self):
        """Test board initialization."""
        board = Board()
        self.assertEqual(len(board.board), 6)
        self.assertEqual(len(board.board[0]), 7)
    
    def test_place_piece(self):
        """Test placing a piece."""
        board = Board()
        self.assertTrue(board.place_piece(0, Board.PLAYER1))
        self.assertEqual(board.board[5][0], Board.PLAYER1)
    
    def test_column_full(self):
        """Test column full detection."""
        board = Board()
        for _ in range(6):
            board.place_piece(0, Board.PLAYER1)
        self.assertTrue(board.is_column_full(0))
    
    def test_invalid_column(self):
        """Test invalid column handling."""
        board = Board()
        self.assertFalse(board.place_piece(-1, Board.PLAYER1))
        self.assertFalse(board.place_piece(7, Board.PLAYER1))


class WinCheckerTestCase(TestCase):
    """Test win detection."""
    
    def test_horizontal_win(self):
        """Test horizontal win detection."""
        board = Board()
        for col in range(4):
            board.place_piece(col, Board.PLAYER1)
        winner = WinChecker.check_winner(board)
        self.assertEqual(winner, Board.PLAYER1)
    
    def test_vertical_win(self):
        """Test vertical win detection."""
        board = Board()
        for _ in range(4):
            board.place_piece(0, Board.PLAYER1)
        winner = WinChecker.check_winner(board)
        self.assertEqual(winner, Board.PLAYER1)
    
    def test_no_winner(self):
        """Test no winner scenario."""
        board = Board()
        board.place_piece(0, Board.PLAYER1)
        board.place_piece(1, Board.PLAYER2)
        winner = WinChecker.check_winner(board)
        self.assertIsNone(winner)


class GameEngineTestCase(TestCase):
    """Test game engine."""
    
    def test_new_game(self):
        """Test new game initialization."""
        engine = GameEngine()
        state = engine.get_state()
        self.assertEqual(state['status'], 'playing')
        self.assertEqual(state['current_player'], Board.PLAYER1)
    
    def test_make_move(self):
        """Test making a move."""
        engine = GameEngine()
        result = engine.make_move(0)
        self.assertTrue(result['success'])
        self.assertEqual(result['state']['current_player'], Board.PLAYER2)
    
    def test_invalid_move(self):
        """Test invalid move handling."""
        engine = GameEngine()
        result = engine.make_move(-1)
        self.assertFalse(result['success'])
    
    def test_win_detection(self):
        """Test win detection in game engine."""
        engine = GameEngine()
        # Make moves to create a win
        for col in range(4):
            engine.make_move(col)  # Player 1
            engine.make_move(col)  # Player 2
        state = engine.get_state()
        self.assertEqual(state['status'], 'won')
        self.assertEqual(state['winner'], Board.PLAYER1)
