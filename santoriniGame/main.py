import pygame
import time  # Import time module





from constants import WIDTH, HEIGHT, SQUARE_SIZE, BLUE, RED, GREY, GREEN
from game import Game
from bot import Bot
from TylerMiniMax.TylerMiniMax import TylerMiniMax
from YaseminsMiniMax.YaseminsMiniMax import YaseminsMiniMax
from ColbysMiniMax.ColbysMiniMax import *


FPS = 60


WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Santorini')

def get_row_col_from_mouse(pos: tuple[int, int]):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def draw_menu(win, buttons):
    win.fill(GREEN)
    
    # Draw buttons
    for button in buttons:
        pygame.draw.rect(win, button["color"], button["rect"])
        font = pygame.font.SysFont(None, 36)
        text = font.render(button["text"], True, (255, 255, 255))
        text_rect = text.get_rect(center=button["rect"].center)
        win.blit(text, text_rect)

    pygame.display.update()

def choose_game_mode():
    """Displays the menu and waits for the user to select a game mode."""
    pygame.init()

    clock = pygame.time.Clock()
    run = True

    button_width, button_height = 400, 100
    buttons = [
        {
            "rect": pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 4 - button_height, button_width, button_height),
            "color": BLUE,
            "text": "Play as Blue vs Red Bot",
            "action": "PvC"
        },
        {
            "rect": pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 - button_height - 40, button_width, button_height),
            "color": RED,
            "text": "Play as Red vs Blue Bot",
            "action": "CvP"
        },
        {
            "rect": pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT * 3 // 4 - button_height - 60, button_width, button_height),
            "color": GREY,
            "text": "Play Locally with a Friend",
            "action": "PvP"
        },
        {
            "rect": pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT - button_height - 80, button_width, button_height),
            "color": GREY,
            "text": "Bot VS Bot",
            "action": "CvC"
        }
    ]

    while run:
        draw_menu(WIN, buttons)
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button["rect"].collidepoint(pos):
                        return button["action"]

    pygame.quit()
    return None


def main():
    pygame.init()

    game_mode = choose_game_mode()

    if game_mode is None:
        return

    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    # Initialize bots
    if game_mode == "PvP":
        blue_player = None
        red_player = None
    elif game_mode == "CvP":
        blue_player = YaseminsMiniMax(game, BLUE, RED)
        red_player = None
    elif game_mode == "PvC":
        blue_player = None
        red_player = YaseminsMiniMax(game,RED,BLUE)
    else:
        blue_player = Bot(game,BLUE,RED)
        red_player = YaseminsMiniMax(game,RED,BLUE)


        num_games = 10
        red_wins, blue_wins = (0, 0)
        blue_turns = 0
        red_turns = 0
        blue_time_total = 0
        red_time_total = 0

        for _ in range(num_games):
            game.reset()
            game.game_over = None

            # Time tracking for each player
            

            # Start tracking turns
            turn_start_time = time.time()

            while game.game_over is None:
                clock.tick(FPS)

                if game.turn == RED:
                    red_player.make_move()

                    # Calculate time spent on RED's turn
                    turn_end_time = time.time()
                    red_time_total += (turn_end_time - turn_start_time)
                    turn_start_time = turn_end_time  # Reset for next turn
                    red_turns += 1
                else:
                    blue_player.make_move()

                    # Calculate time spent on BLUE's turn
                    turn_end_time = time.time()
                    blue_time_total += (turn_end_time - turn_start_time)
                    turn_start_time = turn_end_time  # Reset for next turn
                    blue_turns += 1

                game.update()

            if game.game_over == 'RED':
                red_wins += 1
                winner = 'RED'
            else:
                blue_wins += 1
                winner = 'BLUE'

            # Print the winner and time spent
            print(f"Winner: {winner}")
            print(f"RED total time: {red_time_total:.2f} seconds")
            print(f"BLUE total time: {blue_time_total:.2f} seconds")
            print(f"BLUE avg time per turn {blue_time_total/blue_turns:.2f}")

        print(f"RED Wins: {red_wins}")
        print(f"BLUE Wins: {blue_wins}")
        run = False

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN and game_mode != "CvC":
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                if not game.select(row, col):
                    game.selected = None

        if game.game_over is not None:
            game.reset()
            game.game_over = None
        elif game_mode == "PvC" and game.turn == RED and game.game_over is None:
            red_player.make_move()
        elif game_mode == "CvP" and game.turn == BLUE and game.game_over is None:
            blue_player.make_move()
        elif game_mode == "CvC" and game.game_over is None:
            if game.turn == RED:
                red_player.make_move()
            else:
                blue_player.make_move()

        game.update()

    pygame.quit()

if __name__ == "__main__":
    main()
