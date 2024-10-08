import random
import math

class Bot_mmy:
    def __init__(self, game, own_color, opp_color):
        self.game = game  # Reference to the Game object
        self.own_color = own_color  # Bot's color (BLUE or RED)
        self.opp_color = opp_color

    def make_move(self):
        # Get all pieces for the bot's color
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)
        tile_levels = self.game.board.get_tile_levels()
        if not own_pieces:
            return  # No pieces to move

        # Loop for every valid move and build for each piece and pick the best move
        best_score = float('-inf')
        best_results = []

        for piece in own_pieces:
            valid_moves = self.game.board.get_valid_moves(piece)
            if self.game.select(piece.row, piece.col):  # Simulate piece selection

                for move in valid_moves:
                    row, col = move                     # Simulate move
                    self.game._move(row, col)

                    # Evaluate each (move, build) result
                    valid_builds = self.game.board.get_valid_builds(self.game.selected)
                    for build in valid_builds:
                        score = self.evaluate_result(move, build)

                        if score > best_score:
                            best_score = score
                            best_results = [ (move, build) ]
                        elif score == best_score:
                            best_results.append( (move, build) )

                    row = -row
                    col = -col
                    self.game._move(row, col)           # Undo simulated move
        
        # Pick any result with the highest evaluated score
        if best_results:
            chosen_result = random.choice(best_results)
            row, col = chosen_result[0]
            self.game._move(row, col)                 # Move to chosen (row, col)
            build_row, build_col = chosen_result[1]   # Build on chosen (row, col)
            self.game._build(build_row, build_col)
        self.game.selected = None                     # Deselect after the move and build

    def evaluate_result(self, move, build):
        # For now, let all options evaluate equally
        return 1