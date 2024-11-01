import pygame
import copy

from constants import *
from pieces import Piece


HIGHLIGHT_COLOR = (0, 255, 0, 128)  # Green with some transparency
#test
class Board:



    def __init__(self):
        self.board: list[Piece] = []  # 1-D list of pieces
        self.tile_levels = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # Track tile levels
        self.create_board()
        #self.font = pygame.font.SysFont(None, 36)  # Font for displaying tile levels


    def copy(self):
        return copy.deepcopy(self)


    def draw(self, win: pygame.SurfaceType, valid_moves: dict[tuple[int, int], int] = None):
        win.fill(GREEN)

        # Draw the grid
        for row in range(ROWS):
            for col in range(COLS):
                # Calculate the position for each square
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE

                # Draw the square border
                pygame.draw.rect(win, GREY, (x, y, SQUARE_SIZE, SQUARE_SIZE), 2)

                #Draw blocks
                if self.tile_levels[row][col] >= 1:
                    pygame.draw.rect(win, GREY, (x+(BUFFER/2),y+(BUFFER/2),SQUARE_SIZE-BUFFER,SQUARE_SIZE-BUFFER))
                if self.tile_levels[row][col] >= 2:
                    pygame.draw.rect(win, LIGHT_GREY,(x + (BUFFER), y + (BUFFER), SQUARE_SIZE - (2 * BUFFER), SQUARE_SIZE - (2 * BUFFER)))
                if self.tile_levels[row][col] >= 3:
                    pygame.draw.rect(win, WHITE, (x + (1.5 * BUFFER), y + (1.5 * BUFFER), SQUARE_SIZE - (3 * BUFFER), SQUARE_SIZE - (3 * BUFFER)))
                if self.tile_levels[row][col] == 4:
                    pygame.draw.circle(win, LIGHT_BLUE,(x + SQUARE_SIZE//2, y + SQUARE_SIZE//2), PIECE_SIZE)

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

    def get_all_pieces(self, color: tuple[int, int, int]):
        pieces = []
        for piece in self.board:
            if piece is not None and piece.color == color:
                pieces.append(piece)
        return pieces

    def get_tile_level(self, row, col):
        return self.tile_levels[row][col]