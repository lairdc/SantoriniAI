import random
import math

class YaseminsMiniMax:
    def __init__(self, game, own_color, opp_color):
        self.game = game  # Reference to the Game object
        self.own_color = own_color  # Bot's color (BLUE or RED)
        self.opp_color = opp_color

    def make_move(self):
        # Get all pieces for the bot's color
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)

        # Pick even alpha only. Increasing alpha increases accuracy and runtime
        alpha = 4 

        if not own_pieces:
            return  # No pieces to move
        
        # Find the best possible move
        chosen_result, best_score = self.find_best_move(own_pieces, opp_pieces, alpha)

        # Complete actions
        row, col = chosen_result[0]
        self.game._move(row, col)                 # Move to chosen (row, col)
        build_row, build_col = chosen_result[1]   # Build on chosen (row, col)
        self.game._build(build_row, build_col)
        
        self.game.selected = None                     # Deselect after the move and build

    def find_best_move(self, own_pieces, opp_pieces, alpha):
        best_score = float('-inf')
        best_results = []

        # Continue recursively finding the best move for turn alpha > 0
        if (alpha > 0):
            if (alpha % 2 == 0):                # On even alpha, play from our perspective
                current_pieces = own_pieces
            else:
                current_pieces = opp_pieces     # On odd alpha, play from opponents perspective

            # Evaluate the success of each possible (move, build) we can pick
            for piece in own_pieces:
                valid_moves = self.game.board.get_valid_moves(piece)
                if self.game.select(piece.row, piece.col):  # Simulate piece selection

                    for move in valid_moves:
                        row, col = move                     # Simulate move
                        self.game._move(row, col)

                        # Evaluate each (move, build) result
                        valid_builds = self.game.board.get_valid_builds(self.game.selected)
                        for build in valid_builds:
                            self._try_build(build)         # Simulate build

                            score = self.evaluate_result(move, build)

                            # Look at the next move and see if it results in a board state we like
                            alpha -= 1
                            next_result, next_score = self.find_best_move(own_pieces, opp_pieces, alpha)

                            self._destroy(build)           # Undo simulated build

                            if (alpha % 2 == 0): score -= next_score  # Subtract opponent's high scores
                            else: score += next_score                 # Add our high scores

                            if score > best_score:
                                best_score = score
                                best_results = [ (move, build) ]
                            elif score == best_score:
                                best_results.append( (move, build) )

                        row = -row
                        col = -col
                        self.game._move(row, col)           # Undo simulated move
        
        # Return any move resulting in the best board outcomes
        if best_results:
            return ( random.choice(best_results), best_score )
        return ( ( (0, 0), (0, 0) ), best_score )

    def evaluate_result(self, move, build):
        score = 0



        return score

    # Builds at (x, y) of build without ending turn
    def _try_build(self, build):
        row, col = build
        self.game.board.tile_levels[row][col] += 1
        print(f"Trying build at ({row}, {col}), New level: {self.game.board.tile_levels[row][col]}")  # Debugging output

    # Destroys a building at (x, y) of build
    def _destroy(self, build):
        row, col = build
        self.game.board.tile_levels[row][col] -= 1
        print(f"Destroyed at ({row}, {col}), New level: {self.game.board.tile_levels[row][col]}")  # Debugging output