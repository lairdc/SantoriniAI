#### Things to implement
# score_move: If one piece is trapped, allied_piece_index = -1; undefined behavior


import random
import math
from santoriniGame.pieces import Piece
class SpencMiniMax:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int]):
        self.game = game  # Reference to the Game object
        self.own_color = own_color  # Bot's color (BLUE or RED)
        self.opp_color = opp_color

    def score_move(self, board, own_pieces, curr_piece_index, move_x, move_y, opp_pieces):
        # Current piece status
        cur_x = own_pieces[curr_piece_index].get_x()
        cur_y = own_pieces[curr_piece_index].get_y()
        cur_level = board.get_tile_level(cur_x, cur_y)
        move_level = board.get_tile_level(move_x, move_y)

        # Other piece of same color status
        allied_piece_index = -1
        for i in range(len(opp_pieces)):
            if i != curr_piece_index:
                allied_piece_index = i
                break
        allied_x = -1
        allied_y = -1
        allied_level = -1
        if allied_piece_index != -1:
            allied_x = own_pieces[allied_piece_index].get_x()
            allied_y = own_pieces[allied_piece_index].get_y()
            allied_level = board.get_tile_level(cur_x, cur_y)

        # Opponent pieces status
        opp_list_x = []
        opp_list_y = []
        opp_level = []
        for i in range(len(opp_pieces)):
            opp_list_x.append(opp_pieces[i].get_x())
            opp_list_y.append(opp_pieces[i].get_y())
            opp_level.append(board.get_tile_level(opp_pieces[i].get_x(), opp_pieces[i].get_y()))

        # Calculate scores
        # If moving up a level, higher score
        level_score = 0
        if move_level > cur_level:
            level_score += 1

        # If same level or higher as opponent, higher score
        same_level_score = 0
        for i in range(len(opp_level)):
            if move_level >= opp_level[i]:
                level_score += 1

        # Closer to opponent, higher score
        if allied_piece_index != -1 and len(opp_pieces) == 2:
            if curr_piece_index == 0:
                distance_score = -math.sqrt(((opp_pieces[0].get_x()-move_x) ** 2) + ((opp_pieces[0].get_y()-move_y) ** 2))
            else:
                distance_score = -math.sqrt(((opp_pieces[1].get_x() - move_x) ** 2) + ((opp_pieces[1].get_y() - move_y) ** 2))
        else:
            distance_score = -self.dist_from_opp(opp_pieces, move_x, move_y)

        # Score Hierarchy (highest priority on top)
        #   1. Distance from opponent
        #   2. Same level as opponent
        #   3. Moving up levels
        return 5*level_score + 2*same_level_score + 10*distance_score

    # Retrieves the distance of the closest opponent
    def dist_from_opp(self,opp_pieces,action_x,action_y):
        dist = 99.9
        for i in range(len(opp_pieces)):
            cur_dist = math.sqrt(((opp_pieces[i].get_x()-action_x) ** 2) + ((opp_pieces[i].get_y()-action_y) ** 2))
            if cur_dist < dist:
                dist = cur_dist
        print("Dist close: ", int(dist))
        return dist

    def score_build(self, board, build_x, build_y, opp_win_pos, opp_pieces):
        if opp_win_pos is not None and build_x == opp_win_pos[0] and build_y == opp_win_pos[1]:
            return 50000
        tile_level = board.get_tile_level(build_x, build_y)
        if tile_level > 3:
            return -100 * board.get_tile_level(build_x, build_y) + self.dist_from_opp(opp_pieces, build_x, build_y)
        return 100 * board.get_tile_level(build_x, build_y) + self.dist_from_opp(opp_pieces, build_x, build_y)


    def opp_win(self, board, opp_pieces):
        for piece in opp_pieces:
            valid_moves = self.game.board.get_valid_moves(piece)
            for move, level in valid_moves.items():
                if level == 3:
                    return list(move)  # returns [new_row, new_col]
        return None
    def get_best_action(self, board):
        #[piece_index,move_x,move_y,build_x,build_y,score]
        actions = []
        actions_size = -1
        highest_score_index = 0
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)
        for i in range(len(own_pieces)):
            valid_moves = self.game.board.get_valid_moves(own_pieces[i])
            for move in valid_moves:
                score = 0

                #
                piece_x = own_pieces[i].get_x()
                piece_y = own_pieces[i].get_y()
                #
                curr_piece_index = i
                score += self.score_move(board, own_pieces, curr_piece_index, move[0], move[1],opp_pieces)
                fake_piece = Piece(move[0],move[1],self.own_color)
                valid_builds = self.game.board.get_valid_builds(fake_piece)
                for build in valid_builds:
                    score += self.score_build(board, build[0], build[1], self.opp_win(board, opp_pieces), opp_pieces)
                    print(piece_x," : ",piece_y," : ",move[0]," : ",move[1]," : ",build[0]," : ",build[1]," : ",score)
                    actions.append([i,move[0],move[1],build[0],build[1],score])
                    actions_size += 1
                    if score > actions[highest_score_index][5]:
                        highest_score_index = actions_size
                    elif score == actions[highest_score_index][5]:
                        rand = random.randint(0,1)
                        if rand == 0:
                            highest_score_index = actions_size
        if actions_size == -1:
            return None
        else:
            return actions[highest_score_index]

    def make_move(self):
        # Get all pieces for the bot's color
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)

        if not own_pieces:
            return  # No pieces to move

        action = self.get_best_action(self.game.board)
        # Randomly select a piece and valid moves for it
        piece = own_pieces[action[0]]
        valid_moves = self.game.board.get_valid_moves(piece)

        # If there are valid move, pick move
        if action is not None:
            move = [action[1],action[2]]
            row, col = move
            if self.game.select(piece.row, piece.col):  # Simulate piece selection
                self.game._move(row, col)  # Move to a valid position
                build = [action[3],action[4]]
                build_row, build_col = build
                self.game._build(build_row, build_col)
        self.game.selected = None  # Deselect after the move and build