import random
import math
from santoriniGame.pieces import Piece

class TylerMiniMax:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int]):
        self.game = game
        self.own_color = own_color
        self.opp_color = opp_color

    def score_move(self, board, cur_x, cur_y, move_x, move_y, opp_pieces):
        cur_level = board.get_tile_level(cur_x, cur_y)
        move_level = board.get_tile_level(move_x, move_y)
        diff = move_level - cur_level

        if move_level == 3:  # Winning move
            return 100000

        # Calculate score based on level difference
        score = 500 * diff if diff != 0 else 0

        # Factor in the distance from opponents
        return score + self.dist_from_opp(opp_pieces, move_x, move_y)

    def opp_can_move(self, board, opp_pieces, action_x, action_y):
        for piece in opp_pieces:
            valid_moves = self.game.board.get_valid_moves(piece)
            for move in valid_moves.keys():
                if move[0] == action_x and move[1] == action_y:
                    return True
        return False

    def score_build(self, board, build_x, build_y, opp_can_move, opp_pieces):
        tile_level = board.get_tile_level(build_x, build_y)

        if opp_can_move:
            # If opponent can move, prevent their win
            if tile_level == 3:
                return 50000
            elif tile_level == 2:
                return -50000
        else:
            # Build up and away from opponent
            if tile_level < 4:
                return 100 * tile_level + self.dist_from_opp(opp_pieces, build_x, build_y)

        return 0

    def score_build_old_pos(self, board, build_x, build_y, opp_pieces):
        opp_can_move = False
        tile_level = board.get_tile_level(build_x, build_y)
        for piece in opp_pieces:
            # Calculate the difference in both x and y directions
            dx = abs(build_x - piece.get_x())
            dy = abs(build_y - piece.get_y())

            # Check if they are adjacent
            if (dx <= 1 and dy <= 1) and not (dx == 0 and dy == 0):
                #Check if the piece can move to that level
                if tile_level < 4 and (tile_level - board.get_tile_level(piece.get_x(),piece.get_y()) <= 1):
                    opp_can_move = True
                    break

        if opp_can_move:
            # If opponent can move, prevent their win
            if tile_level == 3:
                return 50000
            elif tile_level == 2:
                return -50000
        else:
            # Build up and away from opponent
            if tile_level < 3:
                return 100 * tile_level + self.dist_from_opp(opp_pieces, build_x, build_y)

        return 0

    def dist_from_opp(self, opp_pieces, action_x, action_y):
        # Use squared distances to avoid costly sqrt computation
        min_dist_sq = float('inf')
        for piece in opp_pieces:
            dx = piece.get_x() - action_x
            dy = piece.get_y() - action_y
            dist_sq = dx * dx + dy * dy
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
        return int(math.sqrt(min_dist_sq))

    def get_best_action(self, board):
        actions = []
        highest_score = float('-inf')
        best_action = None

        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)

        for i, piece in enumerate(own_pieces):
            cur_x, cur_y = piece.get_x(), piece.get_y()
            valid_moves = self.game.board.get_valid_moves(piece)

            for move in valid_moves:
                move_x, move_y = move
                move_score = self.score_move(board, cur_x, cur_y, move_x, move_y, opp_pieces)

                # Simulate the piece moving to the new location
                fake_piece = Piece(move_x, move_y, self.own_color)
                valid_builds = self.game.board.get_valid_builds(fake_piece)

                # Also consider building on the current position before moving
                valid_builds[(cur_x, cur_y)] = board.get_tile_level(cur_x, cur_y)

                for build in valid_builds:
                    build_x, build_y = build
                    build_score = 0
                    if build_x == cur_x and build_y == cur_y:
                        build_score = self.score_build_old_pos(board,build_x,build_y,opp_pieces)
                    else:
                        opp_move = self.opp_can_move(board, opp_pieces, build_x, build_y)
                        build_score = self.score_build(board, build_x, build_y, opp_move, opp_pieces)

                    total_score = move_score + build_score
                    action = [i, move_x, move_y, build_x, build_y, total_score]
                    actions.append(action)

                    # Update the best action
                    if total_score > highest_score:
                        highest_score = total_score
                        best_action = action
                    elif total_score == highest_score and random.choice([True, False]):
                        best_action = action

        return best_action

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
