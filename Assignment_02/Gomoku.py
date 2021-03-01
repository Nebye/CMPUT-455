#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection, color_to_string, format_point, point_to_coord
from board_util import GoBoardUtil
from board import GoBoard

import signal
from alphabeta import call_alphabeta
#from minimax import call_minimaxOR


# https://stackoverflow.com/questions/27835524/how-to-handle-python-signal-exception
# signal handler
def handler(signum, frame):
    raise TimeoutException
# timeout exception to handle signal exception 
class TimeoutException(Exception):
    pass
# for handling flags for when time has exceeded/hit timelimit
signal.signal(signal.SIGALRM, handler)


class Gomoku():
    def __init__(self):
        """
        Gomoku player that selects moves randomly from the set of legal moves.
        Passes/resigns only at the end of the game.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        self.name = "GomokuAssignment2"
        self.version = 1.0

    def get_move(self, board, color, timelimit, tTable, hasher):
        outcome, move = self.solve(board, timelimit, tTable, hasher)

        if move is not None:
            return move
        else:
            return GoBoardUtil.generate_random_move(board, color)

    def solve(self, board, timelimit, tTable, hasher):
        board_copy = board.copy()
        # setsAlarm
        signal.alarm(timelimit)
        try:
            score, move = call_alphabeta(board, tTable, hasher)

            if (score == 0):
                return "draw", move
            else:
                if (score > 0):
                    winner = board.current_player
                    return color_to_string(winner), move
                else:
                    winner = GoBoardUtil.opponent(board.current_player)
                    return color_to_string(winner), None
        except (TimeoutException):
            board.load(board_copy)
            return "unknown", None
        finally:
            # Disable Alarm
            signal.alarm(0)


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Gomoku(), board)
    con.start_connection()


if __name__ == "__main__":
    run()