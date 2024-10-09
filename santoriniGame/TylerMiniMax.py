import random
from .pieces import Piece
class TylerMiniMax:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int]):
        self.game = game  # Reference to the Game object
        self.own_color = own_color  # Bot's color (BLUE or RED)
        self.opp_color = opp_color
    def score_move(self, board, cur_x, cur_y, move_x, move_y):
        score = 0
        cur_level = board.get_tile_level(cur_x,cur_y)
        move_level = board.get_tile_level(move_x,move_y)
        diff = move_level - cur_level
        if move_level == 3:
           score = 10000
        elif diff == 0:
            score = 0
        else:
            score = 10 * diff
        return score

    def opp_win(self, board, opp_pieces):
        for piece in opp_pieces:
            valid_moves = self.game.board.get_valid_moves(piece)
            for move, level in valid_moves.items():
                if level == 3:
                    return list(move)  # returns [new_row, new_col]
        return None
    def score_build(self, board, build_x, build_y, opp_win_pos):
        if opp_win_pos is not None and build_x == opp_win_pos[0] and build_y == opp_win_pos[1]:
            return 5000
        else:
            return 10 * board.get_tile_level(build_x, build_y)
    def get_best_actions(self, board):
        #[piece_index,move_x,move_y,build_x,build_y,score]
        actions = []
        actions_size = -1
        highest_score_index = 0
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)
        for i in range(len(own_pieces)):
            valid_moves = self.game.board.get_valid_moves(own_pieces[i])
            score = 0
            for move in valid_moves:
                score += self.score_move(board, own_pieces[i].get_x, own_pieces[i].get_y, move[0], move[1])
                fake_piece = Piece(move[0],move[1],self.own_color)
                valid_builds = self.game.board.get_valid_builds(fake_piece)
                for build in valid_builds:
                    score += self.score_build(board, build[0], build[1], self.opp_win(board, opp_pieces))
                    actions.append([i,move[0],move[1],build[0],build[1],score])
                    actions_size += 1
                    if score >= actions[highest_score_index][5]:
                        highest_score_index = actions_size

    def make_move(self):
        # Get all pieces for the bot's color
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)


        # A list of lists
        # each inner list is a tile on the board in the following form: [x,y,level, piece_present]
        # for piece_present, 0 = no piece, 1 = own_piece, 2 = opp_piece
        # so the list [0,0,2,1] means the top left tile is at level 2 with the bot's own piece present on the tile
        curGameState = self.get_cur_game_state()

        if not own_pieces:
            return  # No pieces to move

        # Randomly select a piece and valid moves for it
        piece = random.choice(own_pieces)
        valid_moves = self.game.board.get_valid_moves(piece)

        # If there are valid moves, pick one randomly and move
        if valid_moves:
            move = random.choice(list(valid_moves)) #Change for AI
            row, col = move
            if self.game.select(piece.row, piece.col):  # Simulate piece selection
                self.game._move(row, col)  # Move to a random valid position

                # Perform a random build after moving
                valid_builds = self.game.board.get_valid_builds(self.game.selected)
                if valid_builds:
                    build = random.choice(list(valid_builds))
                    build_row, build_col = build
                    self.game._build(build_row, build_col)

        self.game.selected = None  # Deselect after the move and build
