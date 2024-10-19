import random
import math
from .pieces import Piece
class TylerMiniMax:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int]):
        self.game = game  # Reference to the Game object
        self.own_color = own_color  # Bot's color (BLUE or RED)
        self.opp_color = opp_color

    # Scores move based on current pos and move pos and where the oppoent pieces are
    def score_move(self, board, cur_x, cur_y, move_x, move_y, opp_pieces):
        cur_level = board.get_tile_level(cur_x,cur_y)
        move_level = board.get_tile_level(move_x,move_y)
        diff = move_level - cur_level
        score = 0
        if move_level == 3:  # Winning move
           score = 100000
        elif diff == 0:  # Staying on the same level
            score = 0
        else:  #Moving level
            score = 500 * diff
        return score + self.dist_from_opp(opp_pieces,move_x,move_y)  # Tries to move far from opponent

    #Checks if the oppoent can move to the given pos
    def opp_can_move(self, board, opp_pieces, action_x, action_y):
        for piece in opp_pieces:
            valid_moves = self.game.board.get_valid_moves(piece)
            for move, level in valid_moves.items():
                if move[0] == action_x and move[1] == action_y:
                    return True
        return False

    # Scores a build pos based on level and where opponent piece are
    def score_build(self, board, build_x, build_y, opp_can_move, opp_pieces):
        tile_level = board.get_tile_level(build_x, build_y)
        score = 0
        # Opponent can move to pos
        if opp_can_move:
            if tile_level == 3:  # Dome opponents winning move
                score = 50000
            elif tile_level == 2:  # Doesn't give winning move to opponent
                score = -50000
        else:
            # Tries building up and away from opponent
            if tile_level > 3:
                score = -100 * board.get_tile_level(build_x, build_y) + self.dist_from_opp(opp_pieces,build_x,build_y)
            else:
                score = 100 * board.get_tile_level(build_x,build_y) + self.dist_from_opp(opp_pieces,build_x,build_y)
        return score

    # Calculates the closest distance an action pos is from a opponent piece as an int
    def dist_from_opp(self,opp_pieces,action_x,action_y):
        dist = 99.9
        for i in range(len(opp_pieces)):
            cur_dist = math.sqrt(((opp_pieces[i].get_x()-action_x) ** 2) + ((opp_pieces[i].get_y()-action_y) ** 2))
            if cur_dist < dist:
                dist = cur_dist
        return int(dist)

    # Gets all possible move and build combinations possible, scores them, and then returns the combination with the highest score
    def get_best_action(self, board):
        # Return type [piece_index,move_x,move_y,build_x,build_y,score]
        actions = []
        actions_size = -1
        highest_score_index = 0
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)
        for i in range(len(own_pieces)):
            valid_moves = self.game.board.get_valid_moves(own_pieces[i])
            for move in valid_moves:
                move_score = self.score_move(board, own_pieces[i].get_x(), own_pieces[i].get_y(), move[0], move[1],opp_pieces)
                # Simulate the piece moving to the location for build
                fake_piece = Piece(move[0],move[1],self.own_color)
                valid_builds = self.game.board.get_valid_builds(fake_piece)
                # Calculates score for the pieces current pos before they moved
                valid_builds[(own_pieces[i].get_x(), own_pieces[i].get_y())] = board.get_tile_level(own_pieces[i].get_x(), own_pieces[i].get_y())
                for build in valid_builds:
                    opp_move = self.opp_can_move(board, opp_pieces, build[0], build[1])
                    build_score = self.score_build(board, build[0], build[1], opp_move, opp_pieces)
                    score = move_score + build_score
                    print(own_pieces[i].get_x()," : ",own_pieces[i].get_y()," : ",move[0]," : ",move[1]," : ",build[0]," : ",build[1]," : ",score)
                    actions.append([i,move[0],move[1],build[0],build[1],score])
                    actions_size += 1
                    if score > actions[highest_score_index][5]:
                        highest_score_index = actions_size
                    elif score == actions[highest_score_index][5]:  # Randomly changes same score actions
                        rand = random.randint(0,1)
                        if rand == 0:
                            highest_score_index = actions_size

        if actions_size == -1:
            return None
        else:
            return actions[highest_score_index]

    def make_move(self):
        own_pieces = self.game.board.get_all_pieces(self.own_color)

        if not own_pieces:
            return  # No pieces to move

        action = self.get_best_action(self.game.board)
        piece = own_pieces[action[0]]

        if action is not None:
            move = [action[1],action[2]]
            row, col = move
            if self.game.select(piece.row, piece.col):  # Simulate piece selection
                self.game._move(row, col)  # Moves bot piece
                build = [action[3],action[4]]
                build_row, build_col = build
                self.game._build(build_row, build_col)
        self.game.selected = None  # Deselect after the move and build
