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
        alpha = 2

        if not own_pieces:
            return  # No pieces to move
        
        # Find the best possible move
        chosen_result, best_score, chosen_piece_index = self.find_best_move(own_pieces, opp_pieces, alpha)
        chosen_piece = own_pieces[chosen_piece_index]

        # Debug output
        # print(f"Received {chosen_result}, and {best_score}, and ({chosen_piece.row}, {chosen_piece.col}) at index {chosen_piece_index}")

        # Perform optimal move and build for current board state
        if self.game.select(chosen_piece.row, chosen_piece.col):   
            row, col = chosen_result[0]
            self.game._move(row, col)                 # Move to chosen (row, col)
            build_row, build_col = chosen_result[1]   # Build on chosen (row, col)
            self.game._build(build_row, build_col)

        self.game.selected = None                 # Deselect after the move and build

        # Fix alignment issues
        for piece in opp_pieces:
            piece.calc_pos()

    def find_best_move(self, own_pieces, opp_pieces, alpha):
        best_score = None
        best_piece_index = -1
        best_results = []

        # Continue recursively finding the best move for turn alpha > 0
        if (alpha > 0):
            current_piece_index = 0
            current_pieces = self.reset_alpha_state(alpha, None, own_pieces, opp_pieces)

            # Evaluate the success of each possible (move, build) we can pick
            for piece in current_pieces:
                row = piece.row
                col = piece.col
                base_row = piece.row
                base_col = piece.col
                base = (base_row, base_col)

                valid_moves = self.game.board.get_valid_moves(piece).copy()
                piece.calc_pos()

                if self.try_selection(row, col):  # Simulate piece selection
                    for move in valid_moves:
                        row, col = move                     # Simulate move
                        self._try_move(move)
                        current_pieces[current_piece_index].row = row
                        current_pieces[current_piece_index].col = col

                        # Evaluate each (move, build) result
                        valid_builds = self.game.board.get_valid_builds(self.game.selected).copy()
                        piece.calc_pos()
                        for build in valid_builds:
                            self._try_build(build)         # Simulate build
                            score = self.evaluate_result(move, build, alpha, opp_pieces)

                            # Simulate the next move and see if it results in a board state preferred by current alpha
                            next_result, next_score, next_piece = self.find_best_move(own_pieces, opp_pieces, alpha - 1)
                            current_pieces = self.reset_alpha_state(alpha, piece, own_pieces, opp_pieces)
                            score += next_score

                            self._destroy(build)           # Undo simulated build

                            replace = False
                            equal = (score == best_score) and (current_piece_index == best_piece_index)
                            
                            if (best_score is None):
                                replace = True
                            elif (alpha % 2 == 0): 
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
            #print(f"Found best score of {best_score} for alpha {alpha}")
            return ( random.choice(best_results), best_score, best_piece_index )
        return ( ( (0, 0), (0, 0) ), 0, 0 )

    def reset_alpha_state(self, alpha, current_piece, own_pieces, opp_pieces):
        current_pieces = []

        if (alpha % 2 == 0):                
            self.game.turn = self.own_color  # On even alpha, play from our perspective
            current_pieces = own_pieces                
        else:
            self.game.turn = self.opp_color  # On odd alpha, play from opponents perspective    
            current_pieces = opp_pieces
        
        if (current_piece is not None): 
            assert self.try_selection(current_piece.row, current_piece.col)
        
        return current_pieces

    def evaluate_result(self, move, build, alpha, opp_pieces):
        score = 0
        move_r, move_c = move
        build_r, build_c = build

        # Prioritize winning the game above all else
        #print(f"Checking {move_r}, {move_c} with value {self.game.board.tile_levels[move_r][move_c]}")
        if self.game.board.tile_levels[move_r][move_c] == 3:
            score = float('inf')
            winner = "player"
            if (alpha % 2 != 0):
                winner = "opponent"
            # print(f"Found a winning move for {winner}")
        
        # Prioritize proximity to higher tiered buildings
        score += self.game.board.tile_levels[move_r][move_c]
        if self.game.board.tile_levels[build_r][build_c] < 4:
            score += self.game.board.tile_levels[build_r][build_c]

        # Prioritize building away from opponent
        for piece in opp_pieces:
            score -= self._dist(build_r, build_c, piece.row, piece.col)

        # Return positive or negative depending on turn alpha
        if (alpha % 2 == 0): return score
        return -score

    def _dist(self, x_1, y_1, x_2, y_2):
        return math.sqrt( pow(x_2 - x_1, 2) + pow(y_2 - y_1, 2))

    def _print_all_pieces(self, own_pieces, opp_pieces):
        #print(f"Own: ({own_pieces[0].row}, {own_pieces[0].col}) and ({own_pieces[1].row}, {own_pieces[1].col}) ... Opp: ({opp_pieces[0].row}, {opp_pieces[0].col}) and ({opp_pieces[1].row}, {opp_pieces[1].col})")
        pieces = self.game.board.get_all_pieces(own_pieces[0].color)
        #for piece in pieces:
            #print(f"Own: {piece.x}, {piece.y}")
        pieces = self.game.board.get_all_pieces(opp_pieces[0].color)
        for piece in pieces:
            print(f"Opp: {piece.x}, {piece.y}")
        print("\n")

    def _try_build(self, build):
        row, col = build
        self.game.board.tile_levels[row][col] += 1
        #print(f"Trying build at ({row}, {col}), New level: {self.game.board.tile_levels[row][col]}")  # Debugging output

    def _destroy(self, build):
        row, col = build
        self.game.board.tile_levels[row][col] -= 1
        #print(f"Destroyed at ({row}, {col}), New level: {self.game.board.tile_levels[row][col]}")  # Debugging output

    def _try_move(self, move):
        row, col = move
        if self.game.selected and (row, col) in self.game.valid_moves:
            self.game.board.move(self.game.selected, row, col)
            self.game.valid_moves = self.game.board.get_valid_builds(self.game.selected)  # Set up for building after moving

    
    def try_selection(self, row: int, col: int):
        piece = self.game.board.get_piece(row, col)
        
        # Select a piece belonging to the current turn
        if piece is not None and piece.color == self.game.turn:
            self.game.selected = piece
            self.game.valid_moves = self.game.board.get_valid_moves(piece)
            return True
        
        return False