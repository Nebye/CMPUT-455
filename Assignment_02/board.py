import numpy as np

from board_util import (
    GoBoardUtil,
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
    PASS,
    is_black_white,
    is_black_white_empty,
    coord_to_point,
    where1d,
    MAXSIZE,
    GO_POINT
)

from evaluation import evaluate

"""
The GoBoard class implements a board and basic functions to play
moves, check the end of the game, and count the acore at the end.
The class also contains basic utility functions for writing a Go player.
For many more utility functions, see the GoBoardUtil class in board_util.py.
The board is stored as a one-dimensional array of GO_POINT in self.board.
See GoBoardUtil.coord_to_point for explanations of the array encoding.
"""
class GoBoard(object):
    def __init__(self, size):
        """
        Creates a Go board of given size
        """
        assert 2 <= size <= MAXSIZE
        self.reset(size)
        self.calculate_rows_cols_diags()

    def reset(self, size):
        """
        Creates a start state, an empty board with given size.
        """
        self.size = size
        self.NS = size + 1
        self.WE = 1
        self.ko_recapture = None
        self.last_move = None
        self.last2_move = None
        self.current_player = BLACK
        self.maxpoint = size * size + 3 * (size + 1)
        self.board = np.full(self.maxpoint, BORDER, dtype=GO_POINT)
        self._initialize_empty_points(self.board)
        self.calculate_rows_cols_diags()

    def load(self, board):
        self.reset(board.size)
        assert self.NS == board.NS
        assert self.WE == board.WE
        self.ko_recapture = board.ko_recapture
        self.last_move = board.last_move
        self.last2_move = board.last2_move
        self.current_player = board.current_player
        assert self.maxpoint == board.maxpoint
        self.board = np.copy(board.board)

    def calculate_rows_cols_diags(self):
        if self.size < 5:
            return
        self.rows = []
        self.cols = []
        for i in range(1, self.size + 1):
            current_row = []
            start = self.row_start(i)
            for pt in range(start, start + self.size):
                current_row.append(pt)
            self.rows.append(current_row)
            
            start = self.row_start(1) + i - 1
            current_col = []
            for pt in range(start, self.row_start(self.size) + i, self.NS):
                current_col.append(pt)
            self.cols.append(current_col)
        
        self.diags = []
        # appended from personal old connect 5 script
        # diag SE 
        start = self.row_start(1)
        for i in range(start, start + self.size):
            diag_SE = []
            pt = i
            while self.get_color(pt) == EMPTY:
                diag_SE.append(pt)
                pt += self.NS + 1
            if len(diag_SE) >= 5:
                self.diags.append(diag_SE)
        # diag SE NE
        for i in range(start + self.NS, self.row_start(self.size) + 1, self.NS):
            diag_SE = []
            diag_NE = []
            pt = i
            while self.get_color(pt) == EMPTY:
                diag_SE.append(pt)
                pt += self.NS + 1
            pt = i
            while self.get_color(pt) == EMPTY:
                diag_NE.append(pt)
                pt += -1 * self.NS + 1
            if len(diag_SE) >= 5:
                self.diags.append(diag_SE)
            if len(diag_NE) >= 5:
                self.diags.append(diag_NE)
        # diag NE
        start = self.row_start(self.size) + 1
        for i in range(start, start + self.size):
            diag_NE = []
            pt = i
            while self.get_color(pt) == EMPTY:
                diag_NE.append(pt)
                pt += -1 * self.NS + 1
            if len(diag_NE) >=5:
                self.diags.append(diag_NE)
        assert len(self.rows) == self.size
        assert len(self.cols) == self.size
        assert len(self.diags) == (2 * (self.size - 5) + 1) * 2

    def copy(self):
        b = GoBoard(self.size)
        assert b.NS == self.NS
        assert b.WE == self.WE
        b.ko_recapture = self.ko_recapture
        b.last_move = self.last_move
        b.last2_move = self.last2_move
        b.current_player = self.current_player
        assert b.maxpoint == self.maxpoint
        b.board = np.copy(self.board)
        return b

    def get_color(self, point):
        return self.board[point]

    def pt(self, row, col):
        return coord_to_point(row, col, self.size)

    def undo_move(self, move):
        self.board[move] = EMPTY
        self.current_player = GoBoardUtil.opponent(self.current_player)

    def get_best_moves(self):
        moves = self.get_empty_points()
        return sorted(moves, key=self._move_score, reverse=True)

    def _move_score(self, m):
        self.play_move(m, self.current_player)
        score = -self.evaluate()
        self.undo_move(m)
        return score

    def end_of_game(self):
        if self.get_empty_points().size == 0:
            return True
        result = self.detect_five_in_a_row()
        if result == BLACK or result == WHITE:
            return True
        else:
            return False

    def is_legal(self, point, color):
        """
        Check whether it is legal for color to play on point
        This method tries to play the move on a temporary copy of the board.
        This prevents the board from being modified by the move
        """
        board_copy = self.copy()
        can_play_move = board_copy.play_move(point, color)
        return can_play_move

    def get_empty_points(self):
        """
        Return:
            The empty points on the board
        """
        return where1d(self.board == EMPTY)
    
    def get_color_points(self, color):
        """
        Return:
            All points of color on the board
        """
        return where1d(self.board == color)

    def row_start(self, row):
        assert row >= 1
        assert row <= self.size
        return row * self.NS + 1

    def _initialize_empty_points(self, board):
        """
        Fills points on the board with EMPTY
        Argument
        ---------
        board: numpy array, filled with BORDER
        """
        for row in range(1, self.size + 1):
            start = self.row_start(row)
            board[start : start + self.size] = EMPTY

    def evaluate(self):
        win_color = self.detect_five_in_a_row()
        assert win_color != self.current_player

        if win_color != EMPTY:
            return -10000000

        # Heuristic
        return evaluate(self, self.current_player)

    def play_move(self, point, color):
        """
        Play a move of color on point
        Returns boolean: whether move was legal
        """
        assert is_black_white(color)
        # Special cases
        if point == PASS:
            self.ko_recapture = None
            self.current_player = GoBoardUtil.opponent(color)
            self.last2_move = self.last_move
            self.last_move = point
            return True
        elif self.board[point] != EMPTY:
            return False
        self.board[point] = color
        self.current_player = GoBoardUtil.opponent(color)
        self.last2_move = self.last_move
        self.last_move = point
        return True

    def neighbors_of_color(self, point, color):
        """ List of neighbors of point of given color """
        nbc = []
        for nb in self._neighbors(point):
            if self.get_color(nb) == color:
                nbc.append(nb)
        return nbc

    def _neighbors(self, point):
        """ List of all four neighbors of the point """
        return [point - 1, point + 1, point - self.NS, point + self.NS]

    def _diag_neighbors(self, point):
        """ List of all four diagonal neighbors of point """
        return [
            point - self.NS - 1,
            point - self.NS + 1,
            point + self.NS - 1,
            point + self.NS + 1,
        ]

    def last_board_moves(self):
        """
        Get the list of last_move and second last move.
        Only include moves on the board (not None, not PASS).
        """
        board_moves = []
        if self.last_move != None and self.last_move != PASS:
            board_moves.append(self.last_move)
        if self.last2_move != None and self.last2_move != PASS:
            board_moves.append(self.last2_move)
            return 

    def detect_five_in_a_row(self):
        """
        Returns BLACK or WHITE if any five in a row is detected for the color
        EMPTY otherwise.
        """
        for r in self.rows:
            result = self.has_five_in_list(r)
            if result != EMPTY:
                return result
        for c in self.cols:
            result = self.has_five_in_list(c)
            if result != EMPTY:
                return result
        for d in self.diags:
            result = self.has_five_in_list(d)
            if result != EMPTY:
                return result
        return EMPTY

    def has_five_in_list(self, list):
        """
        Returns BLACK or WHITE if any five in a rows exist in the list.
        EMPTY otherwise.
        """
        prev = BORDER
        counter = 1
        for stone in list:
            if self.get_color(stone) == prev:
                counter += 1
            else:
                counter = 1
                prev = self.get_color(stone)
            if counter == 5 and prev != EMPTY:
                return prev
        return EMPTY