import pygame

from santoriniGame.constants import WIDTH, HEIGHT, SQUARE_SIZE, BLUE, RED, GREY, GREEN
from santoriniGame.game import Game
from santoriniGame.bot import Bot
from santoriniGame.SpencMiniMax import SpencMiniMax

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
                return None, None

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button["rect"].collidepoint(pos):
                        return button["action"]  # Return the action associated with the clicked button

    pygame.quit()

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
        blue_player = SpencMiniMax(game, BLUE, RED)
        red_player = None
    elif game_mode == "PvC":
        blue_player = None
        red_player = SpencMiniMax(game,RED,BLUE)
    else:
        blue_player = Bot(game,BLUE,RED)
        red_player = SpencMiniMax(game,RED,BLUE)

    while run:
        clock.tick(FPS)

        # Check if the game is over
        if game.game_over is not None:
            game.game_over = None
            game.reset()
            game.update()

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
        if game_mode == "PvC" and game.turn == RED:
            red_player.make_move()
        elif game_mode == "CvP" and game.turn == BLUE:
            blue_player.make_move()
        elif game_mode == "CvC":
            if game.turn == RED:
                red_player.make_move()
            else:
                blue_player.make_move()


        # Update the display
        game.update()

    pygame.quit()

if __name__ == "__main__":
    main()  # Call the main function to start the game
