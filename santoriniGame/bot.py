import random

class Bot:
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

        # Randomly select a piece and valid moves for it
        piece = random.choice(own_pieces)
        valid_moves = self.game.board.get_valid_moves(piece)

        # If there are valid moves, pick one randomly and move
        if valid_moves:
            move = random.choice(list(valid_moves))
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
