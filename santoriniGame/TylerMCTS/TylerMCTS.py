import random
import math
from santoriniGame.pieces import Piece
from .DictBoard import *
from collections import defaultdict

ROWS = 5
COLS = 5
RED = (255, 0, 0)

class Node:
    def __init__(self, game):
        self.game = game
        self.board = self.board_to_dict(self.game.board)
        self.children = []
        self.visits = 0
        self.wins = 0
        self.parent = None
        self.action = None

    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)

    def board_to_dict(self, old_board):
        dict_board = DictBoard()
        # key is coordinate tuple (0,0) or (2,3) etc
        # value is tuple of (tile level, piece) example: (1, None) or (2, "RED")
        for row in range(ROWS):
            for col in range(COLS):
                tile_level = old_board.get_tile_level(row, col)
                piece = old_board.get_piece(row, col)
                if piece:
                    if piece.color == RED:
                        piece_info = 'RED'
                        dict_board.pieces['RED'].append((row, col))
                    else:
                        piece_info = 'BLUE'
                        dict_board.pieces['BLUE'].append((row, col))
                else:
                    piece_info = None

                dict_board.tiles[(row, col)] = (tile_level, piece_info)

        return dict_board

class TylerMCTS:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int], root):
        self.game = game
        self.own_color = own_color
        self.opp_color = opp_color
        self.root = root

    def select(self, node):
        # Select node with highest UCT value.
        best_child = max(node.children, key=lambda x: (x.wins / x.visits) + (2 * (2 * node.visits) ** 0.5 / x.visits))
        return best_child

    def expand(self, node):



    def make_move(self):
        own_pieces = self.game.board.get_all_pieces(self.own_color)

        if not own_pieces:
            return  # No pieces to move

        action = self.get_best_action(self.game.board)

        if action is not None:
            piece = own_pieces[action[0]]
            move_x, move_y = action[1], action[2]
            build_x, build_y = action[3], action[4]

            if self.game.select(piece.row, piece.col):  # Select piece
                self.game._move(move_x, move_y)  # Move piece
                self.game._build(build_x, build_y)  # Build after move

        self.game.selected = None  # Deselect after move and build
