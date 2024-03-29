from board_util import BLACK, WHITE, EMPTY
import collections

value_coor = [0, 1, 2, 5, 15, 1000000]


def calc_score(counts, color):
    if (color == BLACK):
        my_count, opp_count, open_count = counts
    else:
        opp_count, my_count, open_count = counts
    if (my_count >= 1 and opp_count >= 1):
        return 0
    return value_coor[my_count] - value_coor[opp_count]


def get_counts(board, five_line):
    w_count = 0
    b_count = 0
    e_count = 0    

    for p in five_line:
        stone = board.board[p]
        if (stone == BLACK):
            b_count = b_count + 1
        elif (stone == WHITE):
            w_count = w_count + 1
        else:
            e_count = e_count + 1

    return b_count, w_count, e_count


def evaluate(board, color):
    sPoints = 0
    lines = board.rows + board.cols + board.diags

    for line in lines:
        for i in range(len(line) - 5):
            counts = get_counts(board, line[i:i+5])
            sPoints += calc_score(counts, color)

    return sPoints