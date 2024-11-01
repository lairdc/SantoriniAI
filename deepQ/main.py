import pygame
import numpy as np
import os
import argparse
from deepQ.agent import DQNAgent
from deepQ.board import Board
from deepQ.constants import *

# Filename for saving and loading checkpoints
CHECKPOINT_FILE = "dqn_agent_checkpoint.pth"


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
            return True
        return False

    def display_winner(self, winner_color: tuple[int, int, int]):
        font = pygame.font.SysFont(None, 72)
        win_text = f"{'Blue' if winner_color == BLUE else 'Red'} Wins!"
        text = font.render(win_text, True, (255, 255, 255))  # White text
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.win.blit(text, text_rect)
        pygame.display.update()
        pygame.time.delay(1000)  # Display the message for 1 second

    def change_turn(self):
        self.turn = RED if self.turn == BLUE else BLUE


def extract_state(board):
    """Convert the board state to a numpy array for the agent."""
    state = []
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.get_piece(row, col)
            # Encode pieces by color and tile levels
            if piece is None:
                state.append(0)
            elif piece.color == BLUE:
                state.append(1)  # Blue piece
            else:
                state.append(2)  # Red piece

            # Append the tile level as a feature
            state.append(board.tile_levels[row][col])

    # for i, element in enumerate(state):
    #     print(element, end=" ")
    #     if (i+1) % 2 == 0:
    #         print("| ", end="")
    #     if (i + 1) % 10 == 0:
    #         print()
    # print("\n\n\n\n\n\n")
    return np.array(state)


def run_game(load_checkpoint=True):
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Deep Q-Learning AI Game')
    game = Game(win)

    # Agent setup
    state_size = ROWS * COLS * 2  # Each cell has two values: piece presence and level
    action_size = ROWS * COLS  # Represent each square as an action
    agent = DQNAgent(state_size, action_size)

    # Load checkpoint if specified
    load_checkpoint = True
    if load_checkpoint and os.path.isfile(CHECKPOINT_FILE):
        agent.load_checkpoint(CHECKPOINT_FILE)

    running = True
    clock = pygame.time.Clock()

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Convert the current board state to a numpy array for the agent
            state = extract_state(game.board)

            # Agent chooses an action
            action = agent.act(state)

            # Map action to row and col
            row = action // COLS
            col = action % COLS

            # Select the piece or build
            if game.move:
                reward = 1 if game.select(row, col) else -1  # Reward/Penalty for move phase
            else:
                reward = 10 if game.select(row, col) else -1  # Reward/Penalty for build phase

            # Get the next state after the move/build
            next_state = extract_state(game.board)

            # Check if the game is over
            if game.game_over:
                reward = 100  # High reward for winning
                running = False

            # Store the experience in memory
            agent.remember(state, action, reward, next_state, game.game_over)

            # Update the game display
            game.update()

            # Train the agent with replay
            agent.replay()

            # Update target model weights periodically
            agent.update_target_model()

            # Cap the frame rate
            clock.tick(30)

    finally:
        # Save the agent's progress on exit
        agent.save_checkpoint(CHECKPOINT_FILE)
        print("Checkpoint saved on exit.")
        pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', action='store_true', help="Load from a checkpoint if available.")
    args = parser.parse_args()
    run_game(load_checkpoint=args.load)
