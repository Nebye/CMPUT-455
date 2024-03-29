from gtp_connection import format_point, point_to_coord

import random

import numpy as np

from board_util import (

    GoBoardUtil,

    BLACK,

    WHITE,

    EMPTY,

    DRAW,

)



nodeid = 0



def mcts_step(mcts_tree):

    selected_node = mcts_tree.select()

    new_node, board_copy = mcts_tree.expand(selected_node)

    wins = mcts_tree.simulate(new_node, board_copy)

    mcts_tree.back_propagate(new_node, wins)



def find(pred, arr):

    for e in arr:

        if (pred(e)):

            return e

    return None



C = 2

NUM_SIMS = 50





class MctsNode:

    def __init__(self, parent, move, color, boardsize):

        global nodeid

        self.id = nodeid

        nodeid += 1



        self.parent = parent

        self.move = move

        self.color = color

        self.boardsize = boardsize



        self.wins = 0

        self.sims = 0

        self.winner = EMPTY

        self.children = []

        self.is_fully_expanded = False



        if (parent is None):

            self.move_list = []

        else:

            self.move_list = parent.move_list.copy()

            self.move_list.append(move)



    def __str__(self):

        return "{} {}/{}".format(format_point(point_to_coord(self.move, self.boardsize)), self.wins, self.sims)        



    def update(self, wins, sims):

        self.wins += wins

        self.sims += sims            



    def set_winner(self, winner):

        self.winner = winner

        self.is_fully_expanded = True



    def add_child(self, child):

        self.children.append(child)   



    def __eq__(self, other):

        return other.id == self.id        



    def winrate(self):

        if (self.sims == 0):

            return 0

        return self.wins / self.sims



    def __repr__(self, level=0):

        ret = "  " * level + str(self) + "\n"

        children = sorted(self.children, key=lambda n: n.winrate(), reverse=True)

        for child in children:

            ret += child.__repr__(level + 1)

        return ret    



    def uct(self):

        if (self.sims == 0):

            return 0



        parent_sims = self.parent.sims if self.parent is not None else self.sims

        return self.winrate() + C * np.sqrt(np.log(parent_sims) / self.sims)





class MctsTree:

    def __init__(self, board, color, rule_policy):

        self.board = board

        self.rule_policy = rule_policy

        self.color = color        

        opp_color = GoBoardUtil.opponent(color)

        self.root = MctsNode(None, None, opp_color, board.size)



    def __str__(self):

        return repr(self.root)        



    def expand(self, node):

        board_copy = self.board.copy()

        for move in node.move_list:

            board_copy.play_move(move, board_copy.current_player)



        if (node.is_fully_expanded):

            return node, board_copy



        num_available_moves = len(board_copy.get_empty_points())        

        already_expanded_moves = set(map(lambda n: n.move, node.children))



        best_moves = self.rule_policy.best_moves(board_copy, board_copy.current_player)

        best_moves = list(map(lambda x: x[0], best_moves))

        next_move = find(lambda el: el not in already_expanded_moves, best_moves)



        board_copy.play_move(next_move, board_copy.current_player)

        opp_color = GoBoardUtil.opponent(node.color)

        new_node = MctsNode(node, next_move, opp_color, self.board.size)

        node.add_child(new_node)



        if (len(node.children) == len(best_moves)):

            node.is_fully_expanded = True

        elif (num_available_moves == 1):

            new_node.is_fully_expanded = True



        return new_node, board_copy



    def select(self):

        current = self.root

        while True:

            if (current == self.root and current.is_fully_expanded):

                choices = current.children

            else:

                choices = [current] + current.children



            filtered_choices = list(filter(lambda n: n.winner == EMPTY, choices))



            if (len(filtered_choices) == 0):

                filtered_choices = choices



            choice_ucts = list(map(lambda n: n.uct(), filtered_choices))

            max_uct_index = np.argmax(choice_ucts)

            next_node = choices[max_uct_index]



            if (next_node == current):

                return current



            current = next_node    



    def simulate(self, node, board_copy):

        if (len(board_copy.get_empty_points()) == 0):

            node.set_winner(DRAW)

            return NUM_SIMS / 2



        wins = 0

        initial_winner = board_copy.check_win(node.move)



        if (initial_winner != EMPTY):

            node.set_winner(initial_winner)

            return NUM_SIMS



        for i in range(NUM_SIMS):

            winner = EMPTY

            moves_played = []



            while (len(board_copy.get_empty_points()) > 0 and winner == EMPTY):

                next_move = GoBoardUtil.generate_random_move(board_copy, board_copy.current_player)

                board_copy.play_move(next_move, board_copy.current_player)

                moves_played.append(next_move)

                last_move = next_move

                winner = board_copy.check_win(last_move)



            for move in moves_played:

                board_copy.undo_move(move)



            if (winner == node.color):

                wins += 1

            elif (winner == EMPTY):

                wins += 0.5



        return wins



    def back_propagate(self, node, wins):

        if (node.winner in (WHITE, BLACK)):

            node.update(wins, NUM_SIMS)

            parentNode = node.parent

            if (parentNode is not None):

                parentNode.set_winner(node.winner)

                wins = -parentNode.wins



                currentNode = parentNode

                while currentNode is not None:

                    currentNode.update(wins, NUM_SIMS)

                    wins = NUM_SIMS - wins

                    currentNode = currentNode.parent



            return



        currentNode = node

        while currentNode is not None:

            currentNode.update(wins, NUM_SIMS)

            wins = NUM_SIMS - wins

            currentNode = currentNode.parent      



    def best_move(self):

        #max robust child

        robust_limit = 2 * NUM_SIMS

        robust_children = list(filter(lambda n: n.sims >= robust_limit, self.root.children))



        if (len(robust_children) == 0):

            robust_children = self.root.children



        scores = list(map(lambda n: n.winrate(), robust_children))

        max_score_index = int(np.argmax(scores))

        return robust_children[max_score_index].move  

