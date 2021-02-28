from board_util import GoBoardUtil
INFINITY = 100000

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



# init call minimaxOR
# TODO - fix this so it calls properly
def call_minimaxOR(rootState, tt, hasher):
    return alphabeta(rootState, -INFINITY, INFINITY, tt, hasher)

# TODO - fix this so it stores properly
def storeResult(tt, code, result):
    tt.store(code, result)
    return result