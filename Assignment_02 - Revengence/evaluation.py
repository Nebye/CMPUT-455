from board_util import BLACK, WHITE, EMPTY
import collections

POINTS = [0, 1, 2, 5, 15, 1000000]


def calc_score(counts, color):
    if (color == BLACK):
        my_count, opp_count, open_count = counts
    else:
        opp_count, my_count, open_count = counts
    if (opp_count >= 1 and my_count >= 1):
        return 0
    return POINTS[my_count] - POINTS[opp_count]


def get_counts(board, five_line):
    b_count, w_count, e_count = 0

    for i in five_line:
        stone = board.board[i]
        if stone == BLACK:
            b_count = b_count + 1
        elif stone == WHITE:
            w_count = w_count + 1
        else:
            e_count = e_count + 1
    return b_count, w_count, e_count


def evaluate(board, color):
    lines = board.rows + board.cols + board.diags
    score = 0

    for line in lines:
        for x in range(len(line) - 5):
            counts = get_counts(board, line[x:x+5])
            score = score + calc_score(counts, color)
    return score
