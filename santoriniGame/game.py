import pygame

from board import Board
from constants import *


class Game:
    def __init__(self, win: pygame.SurfaceType):
        self._init()
        self.win = win
        self.game_over = None  # Start with None, to be set as 'BLUE' or 'RED' on win

    def update(self):
        self.board.draw(self.win, self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = BLUE
        self.valid_moves = {}
        self.move = True  # Start in move phase
        self.game_over = None  # Reset game_over state on initialization

    def reset(self):
        self._init()

    def select(self, row: int, col: int):
        piece = self.board.get_piece(row, col)

        if self.selected:
            if self.move:  # Move phase
                if (row, col) in self.valid_moves:
                    self._move(row, col)
                    return True
                else:
                    # Deselect the piece if the move is invalid
                    self.selected = None
                    self.valid_moves = {}
            else:  # Build phase
                if (row, col) in self.valid_moves:
                    self._build(row, col)
                return True
        else:
            # Select a piece belonging to the current turn
            if piece is not None and piece.color == self.turn:
                self.selected = piece
                self.valid_moves = self.board.get_valid_moves(piece)
                return True

        return False

    def _build(self, row, col):
        self.board.tile_levels[row][col] += 1
        print(f"Built at ({row}, {col}), New level: {self.board.tile_levels[row][col]}")  # Debugging output
        self.valid_moves = {}
        self.move = True  # Reset to move phase
        self.change_turn()  # Change turn after building
        self.selected = None  # Deselect after building

    def _move(self, row: int, col: int):
        if self.selected and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)

            # Check if the piece moved onto a level 3 tile
            if self.board.tile_levels[row][col] == 3:
                self.display_winner(self.turn)  # Display winning message
                self.game_over = 'BLUE' if self.turn == BLUE else 'RED'  # Set game_over to winning color
                return True

            self.valid_moves = self.board.get_valid_builds(self.selected)  # Set up for building after moving
            self.move = False  # Switch to build phase
            print(f"Moved to ({row}, {col})")  # Debugging output
            return True
        return False

    def display_winner(self, winner_color: tuple[int, int, int]):
        font = pygame.font.SysFont(None, 72)
        win_text = f"{'Blue' if winner_color == BLUE else 'Red'} Wins!"
        text = font.render(win_text, True, (255, 255, 255))  # White text
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.win.blit(text, text_rect)
        pygame.display.update()
        pygame.time.delay(1000)  # Display the message for 3 seconds

    def change_turn(self):
        self.turn = RED if self.turn == BLUE else BLUE
        print(f"Turn changed to {'Red' if self.turn == RED else 'Blue'}")  # Debugging output