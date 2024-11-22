import pygame

from santoriniGame.constants import WIDTH, HEIGHT, SQUARE_SIZE, BLUE, RED, GREY, GREEN
from santoriniGame.game import Game
from santoriniGame.bot import Bot
from santoriniGame.ColbysMiniMax import ColbysMiniMax

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

    # Initialize bots for different modes
    if game_mode == "PvP":
        blue_player = None
        red_player = None
    elif game_mode == "CvP":
        blue_player = Bot(game, BLUE, RED, use_dqn=True)  # Use DQN for blue
        red_player = None
    elif game_mode == "PvC":
        blue_player = None
        red_player = Bot(game, RED, BLUE, use_dqn=True)  # Use DQN for red
    else:  # CvC
        blue_player = Bot(game, BLUE, RED, use_dqn=True)  # DQN vs Random
        red_player = Bot(game, RED, BLUE, use_dqn=False)

    while run:
        clock.tick(FPS)

        if game.game_over is not None:
    # Give the AI a chance to learn from the game result
            if game_mode == "PvC" and red_player and hasattr(red_player, 'agent'):
                print("Red player learning from game result...")
                red_player.agent.save_model()
            elif game_mode == "CvP" and blue_player and hasattr(blue_player, 'agent'):
                print("Blue player learning from game result...")
                blue_player.agent.save_model()
            elif game_mode == "CvC":
                if game.turn == RED and hasattr(red_player, 'agent'):
                    print("Red player learning from game result...")
                    red_player.agent.save_model()
                elif hasattr(blue_player, 'agent'):
                    print("Blue player learning from game result...")
                    blue_player.agent.save_model()
                    
            # Then reset the game
            pygame.time.delay(2000)  # Give time to see the winner
            game.game_over = None
            game.reset()
            game.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN and game_mode != "CvC":
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                if not game.select(row, col):
                    game.selected = None

        # Bot moves
        if game_mode == "PvC" and game.turn == RED:
            red_player.make_move()
        elif game_mode == "CvP" and game.turn == BLUE:
            blue_player.make_move()
        elif game_mode == "CvC":
            if game.turn == RED:
                red_player.make_move()
            else:
                blue_player.make_move()

        game.update()

    pygame.quit()

if __name__ == "__main__":
    main()
