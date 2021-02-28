import random

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