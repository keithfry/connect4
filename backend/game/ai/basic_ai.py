"""
Basic AI implementation using minimax algorithm.
"""

from typing import Optional
from ..board import Board
from ..win_checker import WinChecker


class BasicAI:
    """Basic AI player using minimax algorithm."""
    
    def __init__(self, depth: int = 4):
        """
        Initialize AI.
        
        Args:
            depth: Search depth for minimax algorithm.
        """
        self.depth = depth
        self.player = Board.PLAYER2  # AI is typically player 2
    
    def set_player(self, player: int):
        """Set which player the AI is."""
        self.player = player
    
    def get_move(self, board: Board, current_player: int) -> int:
        """
        Get the best move for the current player.
        
        Args:
            board: Current board state
            current_player: Current player (1 or 2)
        
        Returns:
            Column index for best move.
        """
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0
        
        best_move = valid_moves[0]
        best_score = float('-inf')
        
        for move in valid_moves:
            test_board = Board(board.get_board())
            test_board.place_piece(move, current_player)
            
            # Check if this move wins
            winner = WinChecker.check_winner(test_board)
            if winner == current_player:
                return move
            
            score = self._minimax(test_board, self.depth - 1, False, current_player)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _minimax(self, board: Board, depth: int, maximizing: bool, ai_player: int) -> int:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board: Current board state
            depth: Remaining search depth
            maximizing: True if maximizing player's turn
            ai_player: AI player number
        
        Returns:
            Score for the position.
        """
        winner = WinChecker.check_winner(board)
        opponent = Board.PLAYER1 if ai_player == Board.PLAYER2 else Board.PLAYER2
        
        if winner == ai_player:
            return 1000 + depth  # Prefer faster wins
        elif winner == opponent:
            return -1000 - depth  # Avoid faster losses
        elif board.is_full() or depth == 0:
            return self._evaluate_board(board, ai_player)
        
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return 0
        
        if maximizing:
            max_score = float('-inf')
            for move in valid_moves:
                test_board = Board(board.get_board())
                test_board.place_piece(move, ai_player)
                score = self._minimax(test_board, depth - 1, False, ai_player)
                max_score = max(max_score, score)
            return max_score
        else:
            min_score = float('inf')
            for move in valid_moves:
                test_board = Board(board.get_board())
                test_board.place_piece(move, opponent)
                score = self._minimax(test_board, depth - 1, True, ai_player)
                min_score = min(min_score, score)
            return min_score
    
    def _evaluate_board(self, board: Board, ai_player: int) -> int:
        """
        Evaluate board position heuristically.
        
        Args:
            board: Board to evaluate
            ai_player: AI player number
        
        Returns:
            Heuristic score.
        """
        score = 0
        opponent = Board.PLAYER1 if ai_player == Board.PLAYER2 else Board.PLAYER2
        board_state = board.get_board()
        
        # Check for potential 3-in-a-row and 2-in-a-row patterns
        # This is a simplified heuristic
        for row in range(Board.ROWS):
            for col in range(Board.COLS):
                if board_state[row][col] == ai_player:
                    score += 1
                elif board_state[row][col] == opponent:
                    score -= 1
        
        return score

