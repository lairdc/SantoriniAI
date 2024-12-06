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

        # Debug output
        print(f"Received {play})")

        # Select piece
        piece = None
        if (pos[0] == own_pieces[0].row and pos[1] == own_pieces[0].col):
            piece = own_pieces[0]
        else:
            piece = own_pieces[1]

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

            valid_plays = self.get_valid_plays(piece)

            # Explore valid plays in MCTS tree
            for play in valid_plays:

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

        return best_play

    # Returns a list of every valid move, build combination for the given piece. 
    # play = ( (piece.row, piece.col), (move.row, move.col), (build.row, build.col))
    def get_valid_plays(self, piece):
        plays = []

        moves = self.game.board.get_valid_moves(piece)
        for move in moves:

            # simulate move
            pieces = self.game.board.get_all_pieces(self.own_color) + self.game.board.get_all_pieces(self.opp_color)
            piece_locations = []
            for p in pieces:
                if piece.row == p.row and piece.col == p.col:
                    piece_locations.append(move)
                else:
                    p_loc = p.row, p.col
                    piece_locations.append(p_loc)

            # append all valid builds based on simulation
            builds = self.mcts_all_valid_builds(move, piece_locations)
            for build in builds:
                location = piece.row, piece.col
                play = location, move, build
                plays.append(play)

        return plays

    # A version of board.py's get_valid_builds but it recieves every piece location in a list
    # This is to bypass piece move/build steps so that we do not break turn order
    def mcts_all_valid_builds(self, move, pieces):

        builds = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Top-left, top, top-right
            (0, -1),         (0, 1),     # Left,         , right
            (1, -1), (1, 0), (1, 1)      # Bottom-left, bottom, bottom-right
        ]

        tile_levels = self.game.board.tile_levels.copy()
        ROWS = len(tile_levels)
        COLS = len(tile_levels[0]) if ROWS > 0 else 0

        for direction in directions:
            new_row = move[0] + direction[0]
            new_col = move[1] + direction[1]
            build = new_row, new_col

            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                target_level = tile_levels[new_row][new_col]

                # Ensure the target level is climbable and does not have a dome
                if target_level < 4:

                    # Check if there is already a piece at the target location
                    valid = True
                    for piece in pieces:
                        if build[0] == piece[0] and build[1] == piece[1]:
                            valid = False

                    if valid:
                        builds.append(build)

        return builds

    # Call this function to save the game data into MCTS search tree
    def analyse_game(self):
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)
        pieces = own_pieces + opp_pieces
        tile_levels = self.game.board.tile_levels
        winner = None

        # Check for winning pieces
        for piece in pieces:
            piece_level = tile_levels[piece.row][piece.col]            
            if piece_level == 3:
                winner = piece
                break
        
        # Check if player lost by having no remaining plays
        own_plays = self.get_valid_plays(own_pieces[0]) + self.get_valid_plays(own_pieces[1])
        if not own_plays:
            # Pick any piece from opposing team as "winner"
            winner = opp_pieces[0]
        opp_plays = self.get_valid_plays(opp_pieces[0]) + self.get_valid_plays(opp_pieces[1])
        if not opp_plays:
            # Pick any pieces from own team as "winner"
            winner = own_pieces[0]

        # Backpropogate if game over
        if winner is not None:
            win = winner.color == self.own_color   # Whether bot won or not
            last_play = self.mcts.get_current()
            last_play.backpropogate(win)
            #print(f"{win}")

        self.mcts.save_tree()

    # Call this function to reset bot position after a game is played
    def reset_tree(self):
        self.mcts.reset()