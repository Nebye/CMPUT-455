#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil, PASS, EMPTY, BLACK, WHITE
from board import GoBoard
import random
import numpy as np

import cProfile

WIN = 4
BLOCK_WIN = 3
OPEN_FOUR = 2
BLOCK_OPEN_FOUR = 1
RANDOM = 0

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
        self.simu = 10
        self.name = "GomokuAssignment3"
        self.version = 1.0

    def get_move(self, board, color):
        moveWinCount = []
        emptyPts = board.get_empty_points()
        #if there are no moves to pick from then pass
        if emptyPts.size == 0:
            return None

        #how many times the move has won
        best = self.rule_based_moves(board, color)
        for number, move in best:
            winCount = self.sim_move(board, move, color)
            moveWinCount.append(winCount)
        #choose best 
        max_ = np.argmax(moveWinCount)
        return best[max_][1]

    def simulate(self, board, move, color):
        passCounter = 0
        board = board.copy()
        board.play_move(move, color)        
        
        #sim entire game
        while board.get_empty_points().size > 0:
            color = board.current_player
            best = self.rule_based_moves(board, color)
            score, move = random.choice(best)

            #return winner color
            if score == WIN:
                return color

            board.play_move(move, color)
            #If move is equal is to passCounter then increment by 1
            #if passCounter is greater than 1
            #else reset passCounter
            if move == PASS:
                passCounter = passCounter + 1  
            elif passCounter > 1:
                break
            else:
                passCounter = 0           

    
    def sim_move(self, board, move, color):
        winCount = 0
        #self.simu = 10
        #simulate move self.simu times        
        for number in range(self.simu):
            counter = self.simulate(board, move, color)
            if counter == color:
                winCount = winCount + 1   
        return winCount    

    def rule_based_moves(self, board, color):
        results = []
        best = []
        bestScore = RANDOM
        
        for move in board.get_empty_points():
            score = self.check_move(board, color, move)
            results.append((score, move))
        results.sort(reverse = True, key = lambda x: x[0])

        #Best move
        for move in results:
            if move[0] > bestScore:
                bestScore = move[0]
            elif move[0] < bestScore:
                break
            best.append(move)
        return best

    def check_move(self, board, color, move):
        """
        returns:
            4 if winning
            3 if block win
            2 if open four
            1 if block open four
            0 otherwise (random)
        """
        board.play_move(move, color)
        newPoint = board.unpadded_point(move)
        lines5 = board.boardLines5[newPoint]
        maxScore = RANDOM        
        lines6 = board.boardLines6[newPoint]
        oppColor = GoBoardUtil.opponent(color)        

        
        for line in lines5:
            counts = board.get_counts(line)
            if color == BLACK:
                myCount, oppCount, openCount = counts
            else:
                oppCount, myCount, openCount = counts
    
            if myCount == 5:
                board.undo_move(move)
                return WIN
            elif oppCount == 4 and myCount == 1:
                maxScore = max(BLOCK_WIN, maxScore)          

        for line in lines6:
            counts = board.get_counts(line)
            if color == BLACK:
                myCount, oppCount, openCount = counts
            else:
                oppCount, myCount, openCount = counts

            firstColor = board.board[line[0]]
            lastColor = board.board[line[-1]]

            if myCount == 4 and firstColor == EMPTY and lastColor == EMPTY:
                maxScore = max(OPEN_FOUR, maxScore)
            elif myCount == 1 and oppCount == 3 and firstColor != oppColor and lastColor != oppColor:
                isBlockOpenFour = False

                colorLine = tuple(map(lambda m: board.board[m], line))
                # must hard code these two cases, they are the only six line patterns that match
                # the above rule, but do not necessarily block an open four
                if colorLine == (color, EMPTY, oppColor, oppColor, oppColor, EMPTY) or \
                   colorLine == (EMPTY, oppColor, oppColor, oppColor, EMPTY, color):

                    # There are alot of edge cases here, so we play the move for
                    # the opposite color and check if they still have an open four available to them
                    # This may break if there are multiple open fours, which wouldn't happen
                    # if the rule based policy is followed throughout the game
                    bestOppMoves = self.rule_based_moves(board, oppColor)
                    # We know there are moves left in this case
                    if bestOppMoves[0][0] < OPEN_FOUR:
                        isBlockOpenFour = True
                else:
                    isBlockOpenFour = True
                
                if isBlockOpenFour:
                    maxScore = max(BLOCK_OPEN_FOUR, maxScore)

        board.undo_move(move)

        return maxScore

def run():
    """
    start the gtp connection and wait for commands.
    """
    board = GoBoard(7)
    con = GtpConnection(Gomoku(), board)
    con.start_connection()
    

if __name__ == "__main__":
    run()
    # cProfile.run('run()')
