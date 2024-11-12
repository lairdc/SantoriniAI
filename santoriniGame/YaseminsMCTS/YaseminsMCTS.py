import random
import math
from .SearchTree import *

class YaseminsMCTS:
    def __init__(self, game, own_color, opp_color):
        self.game = game  # Reference to the Game object
        self.own_color = own_color  # Bot's color (BLUE or RED)
        self.opp_color = opp_color
        self.mcts = SearchTree()
        self.mcts.load_tree()

    def make_move(self):
        # Get all pieces for the bot's color
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)

        if not own_pieces:
            return  # No pieces to move
        
        # Find the best possible move
        play, piece_i = self.make_play()
        piece = own_pieces[piece_i]

        # Debug output
        # print(f"Received {play}, for ({piece.row}, {piece.col}) at index {piece_i}")

        # Perform optimal move and build for current board state
        if self.game.select(piece.row, piece.col):   
            row, col = play[0]
            self.game._move(row, col) 
            build_row, build_col = play[1]            
            self.game._build(build_row, build_col)    

        self.game.selected = None # Deselect piece after finshing turn

        # Fix alignment issues
        for piece in opp_pieces:
            piece.calc_pos()

    def make_play(self):
        return ( ( (0, 0), (0, 0) ), 0 )        