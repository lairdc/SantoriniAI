import pygame

from .constants import *
from .pieces import Piece

HIGHLIGHT_COLOR = (0, 255, 0, 128)  # Green with some transparency
#test
class Board:
    def __init__(self):
        self.board = []  # 1-D list of pieces
        self.tile_levels = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # Track tile levels
        self.create_board()
        self.font = pygame.font.SysFont(None, 36)  # Font for displaying tile levels

    def draw(self, win: pygame.SurfaceType, valid_moves=None):
        win.fill(GREEN)

        # Draw the grid
        for row in range(ROWS):
            for col in range(COLS):
                # Calculate the position for each square
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE

                # Draw the square border
                pygame.draw.rect(win, GREY, (x, y, SQUARE_SIZE, SQUARE_SIZE), 2)

                # Draw the level number on each tile
                level_text = self.font.render(str(self.tile_levels[row][col]), True, (0, 0, 0))
                win.blit(level_text, (x + 5, y + 5))  # Position the text in the top left of each tile

                # Highlight valid moves
                if valid_moves and (row, col) in valid_moves:
                    pygame.draw.circle(win, HIGHLIGHT_COLOR,
                                       (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2), 10)

        # Draw the pieces
        for piece in self.board:
            piece.draw(win)


    def move(self, piece: Piece, row: int, col: int):
        # Update piece location and level
        if piece in self.board:
            self.board.remove(piece)
            new_level = self.tile_levels[row][col]
            piece.move(row, col, new_level)
            self.board.append(piece)

    def get_piece(self, row: int, col: int) -> Piece | None :
        # Check if a piece exists at the given row and col
        for piece in self.board:
            if piece.row == row and piece.col == col:
                return piece
        return None

    def create_board(self):
        # Create blue pieces in the corners
        self.board.append(Piece(1, 1, BLUE))  # Top-left corner
        self.board.append(Piece(1, COLS - 2, BLUE))  # Top-right corner

        # Create red pieces in the corners
        self.board.append(Piece(ROWS - 2, 1, RED))  # Bottom-left corner
        self.board.append(Piece(ROWS - 2, COLS - 2, RED))  # Bottom-right corner

    def get_valid_moves(self, piece: Piece):
        moves = {}
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Top-left, top, top-right
            (0, -1),         (0, 1),     # Left,         , right
            (1, -1), (1, 0), (1, 1)      # Bottom-left, bottom, bottom-right
        ]

        for direction in directions:
            new_row = piece.row + direction[0]
            new_col = piece.col + direction[1]

            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                target_level = self.tile_levels[new_row][new_col]

                # Ensure the target level is climbable and does not have a dome
                if target_level < 4 and (target_level - self.tile_levels[piece.row][piece.col] <= 1):
                    # Check if there is already a piece at the target location
                    if not self.get_piece(new_row, new_col):
                        moves[(new_row, new_col)] = target_level

        return moves

    def get_valid_builds(self, piece: Piece):

        builds = {}
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Top-left, top, top-right
            (0, -1),         (0, 1),     # Left,         , right
            (1, -1), (1, 0), (1, 1)      # Bottom-left, bottom, bottom-right
        ]

        for direction in directions:
            new_row = piece.row + direction[0]
            new_col = piece.col + direction[1]

            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                target_level = self.tile_levels[new_row][new_col]

                # Ensure the target level is climbable and does not have a dome
                if target_level < 4:
                    # Check if there is already a piece at the target location
                    if not self.get_piece(new_row, new_col):
                        builds[(new_row, new_col)] = target_level

        return builds
