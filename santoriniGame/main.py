import pygame

from constants import WIDTH, HEIGHT, SQUARE_SIZE, BLUE, RED, GREY, GREEN
from game import Game
from bot import Bot
from ColbysMiniMax import *
from OldMiniMax import *

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

    # Define buttons with their positions, sizes, and actions
    button_width, button_height = 400, 100
    buttons = [
        {
            "rect": pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 4 - button_height, button_width, button_height),
            "color": BLUE,
            "text": "Play as Blue vs Red Bot",
            "action": "PvC" # Player is Blue, Bot is Red
        },
        {
            "rect": pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 - button_height - 40, button_width, button_height),
            "color": RED,
            "text": "Play as Red vs Blue Bot",
            "action": "CvP"  # Player is Red, Bot is Blue
        },
        {
            "rect": pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT * 3 // 4 - button_height - 60, button_width, button_height),
            "color": GREY,
            "text": "Play Locally with a Friend",
            "action": "PvP"  # Local multiplayer, no bots
        },
        {
            "rect": pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT - button_height - 80, button_width, button_height),
            "color": GREY,
            "text": "Bot VS Bot",
            "action": "CvC"  # Bot vs Bot game mode
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
                        return button["action"]  # Return the action associated with the clicked button

    pygame.quit()
    return None  # Ensure a return even if the loop ends without user action


def main():
    pygame.init()

    # Get game mode selection
    game_mode = choose_game_mode()

    if game_mode is None:
        return  # If the user quits during game mode selection

    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    # Initialize bots for Bot VS Bot mode
    if game_mode == "PvP":
        blue_player = None
        red_player = None
    elif game_mode == "CvP":
        blue_player = Bot(game, BLUE, RED)
        red_player = None
    elif game_mode == "PvC":
        blue_player = None
        red_player = ColbysMiniMax(game, RED, BLUE)
    else:  # Bot vs Bot mode
        blue_player = OldMiniMax(game, BLUE, RED)
        red_player = ColbysMiniMax(game, RED, BLUE)


        num_games = 100
        red_wins,blue_wins = (0,0)

        for _ in range(num_games):
            game.reset()
            game.game_over = None

            while game.game_over is None:
                clock.tick(FPS)

                if game.turn == RED:
                    red_player.make_move()
                else:
                    blue_player.make_move()

                game.update()

            if game.game_over == 'RED':
                red_wins += 1
            else:

                blue_wins += 1




        # End game after the simulation

        print(f"RED: {red_wins}")
        print(f"BLUE: {blue_wins}")
        run = False

    while run:
        clock.tick(FPS)

        # Check for user events like quitting or clicking
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN and game_mode != "CvC":
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                # Select or move piece based on current game state
                if not game.select(row, col):
                    game.selected = None  # Reset selected piece

        # Let the bots make their moves if it's the bot's turn
        if game_mode == "PvC" and game.turn == RED and game.game_over is None:
            red_player.make_move()
        elif game_mode == "CvP" and game.turn == BLUE and game.game_over is None:
            blue_player.make_move()
        elif game_mode == "CvC" and game.game_over is None:
            if game.turn == RED:
                red_player.make_move()
            else:
                blue_player.make_move()

        # Update the display
        game.update()

    pygame.quit()

if __name__ == "__main__":
    main()  # Call the main function to start the game
