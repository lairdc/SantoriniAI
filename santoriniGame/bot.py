import random

class Bot:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int]):
        self.game = game  # Reference to the Game object
        self.own_color = own_color  # Bot's color (BLUE or RED)
        self.opp_color = opp_color

    def reset(self):
        self.game = None
        self.own_color = None
        self.opp_color = None

    def make_move(self):
        # Get all pieces for the bot's color
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)


        # A list of lists
        # each inner list is a tile on the board in the following form: [x,y,level, piece_present]
        # for piece_present, 0 = no piece, 1 = own_piece, 2 = opp_piece
        # so the list [0,0,2,1] means the top left tile is at level 2 with the bot's own piece present on the tile
        curGameState = []

        for row in range(5):
            for col in range(5):
                # Get the level of the current tile
                level = self.game.board.get_tile_level(row, col)

                # Determine if a piece is present and who owns it
                piece = self.game.board.get_piece(row, col)
                piece_present = 0  # No piece by default
                if piece:
                    if piece.color == self.own_color:
                        piece_present = 1  # Bot's own piece
                    elif piece.color == self.opp_color:
                        piece_present = 2  # Opponent's piece

                # Add the tile information to curGameState in the form [x, y, level, piece_present]
                curGameState.append([row, col, level, piece_present])



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
