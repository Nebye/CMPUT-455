import sys
import signal
from gtp_connection import GtpConnection
from board_util import GoBoardUtil, PASS, EMPTY, BLACK, WHITE
from board import GoBoard
from evaluation import evaluate
from mcts import MctsTree, mcts_step

import cProfile

WIN = 4
BLOCK_WIN = 3
OPEN_FOUR = 2
BLOCK_OPEN_FOUR = 1
RANDOM = 0

class Gomoku:
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
        self.name = "GomokuAssignment4"
        self.version = 1.0
        self.timelimit = 59

    def set_timeout(self, limit):
        self.timelimit = limit

    def get_move(self, board, color):
        signal.alarm(self.timelimit)  # sets an alarm for the given time_limit

        try:
            mctsTree = MctsTree(board, color, CombinedPolicy())
            while True:
                mcts_step(mctsTree)
                
        except Exception:
            return mctsTree.best_move()        
        except TimeoutException:
            return mctsTree.best_move()
        finally:
            #disable alarm
            signal.alarm(0)

class CombinedPolicy:
    def __init__(self):
        self.rule_policy = RulePolicy()
        self.h_policy = HeuristicPolicy()

    def best_moves(self, board, color):
        rule_best_moves = self.rule_policy.best_moves(board, color)

        # get best moves
        best_score = RANDOM
        best_move = []
        for move in rule_best_moves:
            if move[1] > best_score:
                best_score = move[1]
            if move[1] < best_score or move[1] == RANDOM:
                break
            best_move.append(move)

        if len(best_move) > 0:
            return best_move

        return self.h_policy.best_moves(board, color)
    
class TimeoutException(Exception):
    pass


def handler(signum, frame):
    raise TimeoutException


signal.signal(signal.SIGALRM, handler)    


class HeuristicPolicy:
    
    def _move_score(self, board, color, m):
        board.play_move(m, board.current_player)
        score = evaluate(board, color)
        board.undo_move(m)
        return score    

    def best_moves(self, board, color):
        moves = board.get_empty_points()
        moveResults = list(map(lambda m: (m, self._move_score(board, color, m)), moves))
        return sorted(moveResults, key=lambda r: r[1], reverse=True)


class RulePolicy:

    def check_move(self, board, color, move):
        #5 Random
        #4 BlockOpenFour
        #3 OpenFour
        #2 BlockWin
        #1 Win

        board.play_move(move, color)
        result = RANDOM  
        newPoint = board.unpadded_point(move)
        boardLines5 = board.boardLines5[newPoint]      
        boardLines6 = board.boardLines6[newPoint]
        oppColor = GoBoardUtil.opponent(color)        

        for line in boardLines5:
            counts = board.get_counts(line)
            if (color == BLACK):
                myCount, oppCount, openCount = counts
            else:
                oppCount, myCount, openCount = counts

            if (oppCount == 4 and myCount == 1):
                result = max(BLOCK_WIN, result) 
            elif myCount == 5:
                board.undo_move(move)
                return WIN            

        for line in boardLines6:
            counts = board.get_counts(line)
            if (color == BLACK):
                myCount, oppCount, openCount = counts
            else:
                oppCount, myCount, openCount = counts

            firstColor = board.board[line[0]]
            lastColor = board.board[line[-1]]

            if (firstColor != oppColor and oppCount == 3 and lastColor != oppColor and myCount == 1):
                isBlockOpen = False
                colorLine = tuple(map(lambda m: board.board[m], line))

                #Special cases, do not remove
                if (colorLine == (color, EMPTY, oppColor, oppColor, oppColor, EMPTY) or \
                    colorLine == (EMPTY, oppColor, oppColor, oppColor, EMPTY, color)):

                    #In case rule based policy is not followed
                    #In case of edge cases
                    bestOppMoves = self.rule_based_moves(board, oppColor)
                    if (bestOppMoves[0][0] < OPEN_FOUR):
                        isBlockOpen = True
                else:
                    isBlockOpen = True

                if (isBlockOpen):
                    result = max(BLOCK_OPEN_FOUR, result)
            elif (lastColor == EMPTY and firstColor == EMPTY and myCount == 4):
                result = max(OPEN_FOUR, result)            

        board.undo_move(move)
        return result
    
    def best_moves(self, board, color):
        moveResults = []

        for move in board.get_empty_points():
            moveScore = self.check_move(board, color, move)
            moveResults.append((move, moveScore))

        moveResults.sort(reverse=True, key=lambda x: x[1])
        return moveResults    


def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Gomoku(), board)

    if len(sys.argv) >= 4 and sys.argv[1] == '--pycharm':
        filename = sys.argv[3]
        with open(filename, 'r') as f:
            con.start_connection(f)
    else:
        con.start_connection(sys.stdin)
    

if __name__ == "__main__":
    run()