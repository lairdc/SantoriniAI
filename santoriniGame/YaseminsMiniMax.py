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

        for piece in own_pieces:
            row = piece.row
            col = piece.col
            #self.game._move(row, col)
            #print(f"{row}, {col}")

        # Pick even alpha only. Increasing alpha increases accuracy and runtime
        alpha = 2

        if not own_pieces:
            return  # No pieces to move
        
        # Find the best possible move
        chosen_result, best_score, chosen_piece_index = self.find_best_move(own_pieces, opp_pieces, alpha)
        chosen_piece = own_pieces[chosen_piece_index]
        # print(f"Received {chosen_result}, and {best_score}, and ({chosen_piece.row}, {chosen_piece.col}) at index {chosen_piece_index}")
        # Complete actions
        if self.game.select(chosen_piece.row, chosen_piece.col): 
            # print(f"Moved piece from ({chosen_piece.row}, {chosen_piece.col}) to {chosen_result[0]}")
            row, col = chosen_result[0]
            self.game._move(row, col)                 # Move to chosen (row, col)
            build_row, build_col = chosen_result[1]   # Build on chosen (row, col)
            self.game._build(build_row, build_col)
        # print("NEXT TURN \n\n")
        self.game.selected = None                 # Deselect after the move and build

    def find_best_move(self, own_pieces, opp_pieces, alpha):
        best_score = float('-inf')
        best_piece_index = -1
        best_results = []

        # Continue recursively finding the best move for turn alpha > 0
        if (alpha > 0):
            current_piece_index = 0
            current_pieces = None
            if (alpha % 2 == 0):                # On even alpha, play from our perspective
                current_pieces = own_pieces
            else:
                current_pieces = opp_pieces     # On odd alpha, play from opponents perspective            
            #print(f"On alpha = {alpha}")

            # Evaluate the success of each possible (move, build) we can pick
            for piece in current_pieces:
                row = piece.row
                col = piece.col
                valid_moves = self.game.board.get_valid_moves(piece).copy()
                base_row = piece.row
                base_col = piece.col
                base = base_row, base_col

                if self.try_selection(row, col):  # Simulate piece selection

                    for move in valid_moves:
                        row, col = move                     # Simulate move
                        self._try_move(move)
                        current_pieces[current_piece_index].row = row
                        current_pieces[current_piece_index].col = col

                        # Evaluate each (move, build) result
                        valid_builds = self.game.board.get_valid_builds(self.game.selected).copy()
                        for build in valid_builds:
                            self._try_build(build)         # Simulate build
                            score = self.evaluate_result(move, build, alpha)

                            # Simulate the next move and see if it results in a board state preferred by current alpha
                            next_result = ( (0, 0), (0, 0) )
                            next_score = 0
                            next_piece_index = 0
                            # next_result, next_score, next_piece = self.find_best_move(own_pieces, opp_pieces, alpha - 1)
                            score += next_score

                            self._destroy(build)           # Undo simulated build

                            replace = False
                            equal = (score == best_score) and (current_piece_index == best_piece_index)
                            if (alpha % 2 == 0): 
                                replace = score > best_score        # We want the highest possible score

                            else: 
                                replace = score < best_score        # Opponent wants the lowest possible score

                            if replace:
                                best_score = score
                                best_results = [ (move, build) ]
                                best_piece_index = current_piece_index
                            elif equal:
                                best_results.append( (move, build) )

                        self._try_move(base)           # Undo simulated move

                    # Undo simulated selection
                    self.game.selected = None
                    current_pieces[current_piece_index].row = base_row
                    current_pieces[current_piece_index].col = base_col
                    current_piece_index += 1
                   
                else:
                    print(f"Failed piece selection at {row}, {col}")
                    debug = self.try_selection(row, col)
                    if debug:
                        print("Piece selection should have success")
        
        # Return any move resulting in the best board outcomes
        if best_results:
            return ( random.choice(best_results), best_score, best_piece_index )
        return ( ( (0, 0), (0, 0) ), best_score, 0 )

    def evaluate_result(self, move, build, alpha):
        score = 0
        move_r, move_c = move

        # Prioritize winning the game above all else
        # print(f"Checking {move_r}, {move_c} with value {self.game.board.tile_levels[move_r][move_c]}")
        if self.game.board.tile_levels[move_r][move_c] == 3:
            score = float('inf')
            # print(f"Found a winning move")

        # Prioritize proximity to higher tiered buildings
        # tba

        # Prioritize building away from opponent
        # tba

        # Return positive or negative depending on turn alpha
        if (alpha % 2 == 0): return score
        return -score

    # Builds at (x, y) of build without ending turn
    def _try_build(self, build):
        row, col = build
        self.game.board.tile_levels[row][col] += 1
        #print(f"Trying build at ({row}, {col}), New level: {self.game.board.tile_levels[row][col]}")  # Debugging output

    # Destroys a building at (x, y) of build
    def _destroy(self, build):
        row, col = build
        self.game.board.tile_levels[row][col] -= 1
        #print(f"Destroyed at ({row}, {col}), New level: {self.game.board.tile_levels[row][col]}")  # Debugging output

    # Moves piece to (x, y) of move without ending turn or evaluating winners
    def _try_move(self, move):
        row, col = move
        if self.game.selected and (row, col) in self.game.valid_moves:
            self.game.board.move(self.game.selected, row, col)

            # Check if the piece moved onto a level 3 tile
            #if self.board.tile_levels[row][col] == 3:
                #self.display_winner(self.turn)  # Display winning message
                #self.game_over = 'BLUE' if self.turn == BLUE else 'RED'  # Set game_over to winning color
                #return True

            self.game.valid_moves = self.game.board.get_valid_builds(self.game.selected)  # Set up for building after moving
            #self.move = False  # Switch to build phase
            # print(f"Moved to ({row}, {col})")  # Debugging output
            #return True
        #return False

    
    def try_selection(self, row: int, col: int):
        piece = self.game.board.get_piece(row, col)
        
        # Select a piece belonging to the current turn
        if piece is not None and piece.color == self.game.turn:
            self.game.selected = piece
            self.game.valid_moves = self.game.board.get_valid_moves(piece)
            return True
        
        return False