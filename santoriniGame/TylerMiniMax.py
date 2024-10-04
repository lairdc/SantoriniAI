import random

class TylerMiniMax:
    def __init__(self, game, own_color: tuple[int, int, int], opp_color: tuple[int, int, int]):
        self.game = game  # Reference to the Game object
        self.own_color = own_color  # Bot's color (BLUE or RED)
        self.opp_color = opp_color
    def get_cur_game_state(self, board):
        cur_game_state = []
        for row in range(5):
            for col in range(5):
                # Get the level of the current tile
                level = board.get_tile_level(row, col)

                # Determine if a piece is present and who owns it
                piece = board.get_piece(row, col)
                piece_present = 0  # No piece by default
                if piece:
                    if piece.color == self.own_color:
                        piece_present = 1  # Bot's own piece
                    elif piece.color == self.opp_color:
                        piece_present = 2  # Opponent's piece

                # Add the tile information to cur_game_state in the form [x, y, level, piece_present]
                cur_game_state.append([row, col, level, piece_present])
        return cur_game_state
    def evaluate_tile_moves(self, old_tile, cur_tile, old_game_state, cur_game_state):
        score = 0
        row = old_tile[0]
        col = old_tile[1]
        cur_level = cur_tile[2]
        cur_piece = cur_tile[3]

        return score
    def evaluate_board_moves(self, game_state):
        scoreBoard = [[0 for _ in range(5)] for _ in range(5)]
        for tile in game_state:
            # List of relative coordinates that represent all 8 neighbors plus the center itself
            directions = [(-1, -1), (-1, 0), (-1, 1),
                          (0, -1), (0, 0), (0, 1),
                          (1, -1), (1, 0), (1, 1)]

            # Loop through all 8 directions + the center itself
            for dx, dy in directions:
                # Calculate the coordinates of the surrounding point
                new_x, new_y = tile[0] + dx, tile[1] + dy
                # Check if the new coordinates are within the bounds of the array
                score = 0
                if tile[3] == 1:  # own Color's piece present
                    score += (tile[2] * 5)
                    if (tile[2] == 3):
                        score += 10000
                if 0 <= new_x < 5 and 0 <= new_y < 5 and tile[3] == 1:
                    scoreBoard[new_x][new_y] += score
        return scoreBoard
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
