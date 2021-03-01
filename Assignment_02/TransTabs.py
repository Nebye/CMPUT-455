import random


class TranspositionTable:
    def __init__(self):
        self.table = {}

    def store(self, code, result):
        # result is a tuple: (score, best_move)
        self.table[code] = result

    def lookup(self, code):
        return self.table.get(code)

    def returnTable(self):
        return self.table


class ZobristHasher:

    def __init__(self, boardSize):
        self.zobristArray = []
        self.boardIndices = boardSize*boardSize

        for i in range(self.boardIndices):
            self.zobristArray.append([random.getrandbits(64) for i in range(3)])

    def hash(self, board):
        hashCode = self.zobristArray[0][board[0]]

        for i in range(1,self.boardIndices):
            hashCode = hashCode ^ self.zobristArray[i][board[i]]

        return hashCode