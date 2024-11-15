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
        play = self.make_play()
        pos, move, build = play
        piece = None
        if (pos[0] == own_pieces[0].row and pos[0] == own_pieces[0].col):
            piece = own_pieces[0]
        else:
            piece = own_pieces[1]

        # Debug output
        print(f"Received {play})")

        # Perform optimal move and build for current board state
        if self.game.select(piece.row, piece.col):   
            row, col = move
            self.game._move(row, col) 
            build_row, build_col = build        
            self.game._build(build_row, build_col)    

        # Update tree
        current = self.mcts.get_current()
        chosen = current.get_child(play)
        if chosen is not None:
            self.mcts.move_current(chosen)

        self.game.selected = None # Deselect piece after finshing turn

    def make_play(self):
        # Get all pieces for the bot's color
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        best_play = ( (0, 0), (0, 0), (0, 0) )
        best_ucb1 = float('-inf')

        # Loop for each possible piece, move, and build
        for piece in own_pieces:
            print(f"new piece")
            start_row = piece.row
            start_col = piece.col
            start = start_row, start_col
            if self.game.select(piece.row, piece.col):
                valid_moves = self.game.board.get_valid_moves(piece)
                for move in valid_moves:
                    row, col = move
                    self._try_move(move)
                    valid_builds = self.game.board.get_valid_builds(self.game.selected)
                    for build in valid_builds:
                    
                        # Explore valid plays in MCTS tree
                        play = (start, move, build)
                        print(f"{play}")

                        current = self.mcts.get_current()
                        child = current.get_child(play)
                        if child == None:
                            # New possible move found, add to tree
                            child = TreeNode(play, current)
                            current.add_child(child)

                        # Analyse UCB1 score of current play
                        score = child.ucb1()
                        if score > best_ucb1:
                            best_play = play
                            best_ucb1 = score   
                        
                    print(f"{start[0]}, {start[1]}")
                    self._try_move(start)

        return best_play

    def _try_move(self, move):
        row, col = move
        if self.game.selected and (row, col) in self.game.valid_moves:
            self.game.board.move(self.game.selected, row, col)
            #self.game.valid_moves = self.game.board.get_valid_builds(self.game.selected)  # Set up for building after moving