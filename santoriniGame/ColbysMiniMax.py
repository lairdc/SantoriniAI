import random

class ColbysMiniMax:
    def __init__(self, game, own_color, opp_color):
        self.game = game  # Reference to the Game object
        self.own_color = own_color  # Bot's color (BLUE or RED)
        self.opp_color = opp_color

    def evaluate_board(self, old_game_state, cur_game_state):
        score = 0

        for i in range(len(cur_game_state)) :
            score += evaluate_tile(old_game_state[i],cur_game_state[i])
        return score

    def evaluate_tile(self, old_tile, cur_tile, old_game_state, cur_game_state):
        score = 0
        row = old_tile[0]
        col = old_tile[1]
        old_level = old_tile[2]
        cur_level = cur_tile[2]
        old_piece = old_tile[3]
        cur_piece = cur_tile[3]

        if cur_piece == 2: #opp piece present
            score -= (cur_level * 5)
            if cur_level == 3:
                score -= 1000
        elif cur_piece == 1: #own Color's piece present
            score += (cur_level * 5)
            if (cur_level == 3):
                score += 10000
        else: #no piece present
            if cur_level - old_level == 1:
                if level == 4:
                    score += 5
                else:
                    score += level * 5
        return score

    """function get_children(node):
    # Generate all possible game states from the current node
    children = []
    for each piece in node.pieces:
        for each valid move for piece:
            child = create_new_node(node)
            move_piece(child, piece, valid_move)
            children.append(child)
    return children"""

    def get_children(self,board,turn):
        #generate all possible game state from the current board
        children = []
        pieces = board.get_all_pieces(turn)
        for piece in pieces:
            moves = board.get_valid_moves(piece)
            for move in moves:
                fake_piece = Piece(move[0],move[1],turn)
                builds = get_valid_builds(fake_piece)
                for build in builds:
                    board.move(fake_piece,piece.row, piece.col)
                    board.tile_levels[build[0],build[1]] += 1



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


             

    def make_move(self):
        # Get all pieces for the bot's color
        own_pieces = self.game.board.get_all_pieces(self.own_color)
        opp_pieces = self.game.board.get_all_pieces(self.opp_color)


        # A list of lists
        # each inner list is a tile on the board in the following form: [x,y,level, piece_present]
        # for piece_present, 0 = no piece, 1 = own_piece, 2 = opp_piece
        # so the list [0,0,2,1] means the top left tile is at level 2 with the bot's own piece present on the tile
        cur_game_state = []

        board = self.game.board
        cur_game_state = self.get_cur_game_state(board)



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
