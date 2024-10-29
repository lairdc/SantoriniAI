import pygame

from board import Board
from constants import *
from pieces import Piece



class Game:
    def __init__(self, win: pygame.SurfaceType):
        self._init()
        self.win = win
        self.game_over = None  # Start with None, to be set as 'BLUE' or 'RED' on win

    def update(self):
        self.board.draw(self.win, self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected: Piece | None = None
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
                if self.valid_moves != None and (row, col) in self.valid_moves:
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

    def _build(self, row: int, col: int):
        self.board.tile_levels[row][col] += 1
        #print(f"Built at ({row}, {col}), New level: {self.board.tile_levels[row][col]}")  # Debugging output
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
        self.valid_moves = None
        self.update()
        font = pygame.font.SysFont(None, 72)
        win_text = f"{'Blue' if winner_color == BLUE else 'Red'} Wins!"
        text = font.render(win_text, True, (255, 255, 255))  # White text
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.win.blit(text, text_rect)
        pygame.display.update()
        pygame.time.delay(2000)  # Display the message for 2 seconds
        return winner_color

    def change_turn(self):
        self.turn = RED if self.turn == BLUE else BLUE
        print(f"Turn changed to {'Red' if self.turn == RED else 'Blue'}")  # Debugging output
        
        # Check if the new turn player has valid moves
        if not self.has_valid_moves(self.turn):
            opponent_color = RED if self.turn == BLUE else BLUE
            self.display_winner(opponent_color)  # Display winner message for the opponent
            self.game_over = opponent_color  # Set game_over to winning color
            print(f"{'Red' if opponent_color == RED else 'Blue'} wins by default! No valid moves for {self.turn}.")
    
    def has_valid_moves(self, color):
        """Check if the player with the specified color has any valid moves."""
        pieces = self.board.get_all_pieces(color)  # Get all pieces of the current player
        for piece in pieces:
            if self.board.get_valid_moves(piece):
                return True  # Found a piece with valid moves or builds
        return False  # No valid moves found for any pieces