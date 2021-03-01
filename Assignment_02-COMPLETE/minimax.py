from board_util import GoBoardUtil
INFINITY = 100000
'''
# minimax algorithm (maybe not use)
def minimaxOR(state):
    if state.endOfGame():
        return state.staticallyEvaluate() 
    best = -INFINITY
    for m in state.legalMoves():
        state.play(m)
        value = minimaxAND(state)
        if value > best:
            best = value
        state.undoMove()
    return best

def minimaxAND(state):
    if state.endOfGame():
        return state.staticallyEvaluate() 
    best = INFINITY
    for m in state.legalMoves():
        state.play(m)
        value = minimaxOR(state)
        if value < best:
            best = value
        state.undoMove()
    return best

# init call
# TODO: FIX this 
def call_minimaxOR(rootState, tt, hasher):
    return minimaxOR(rootState, -INFINITY, INFINITY, tt, hasher)

# store results
# TODO: Fix this
def storeResult(tt, code, result):
    tt.store(code, result)
    return result 
'''