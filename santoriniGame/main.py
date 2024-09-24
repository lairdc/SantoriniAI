import pygame

from santoriniGame.constants import WIDTH, HEIGHT, SQUARE_SIZE
from santoriniGame.game import Game

FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Santorini')

def get_row_col_from_mouse(pos: tuple[int, int]):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    pygame.init()

    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(FPS)

        # Check if the game is over
        if game.game_over != None:
            """    
            run = False  # Exit the game loop if the game is over
            continue #this if statement could be tweaked to reset the game instead

            """
            game.game_over = None
            game.reset()
            game.update()


        # Check for user events like quitting or clicking
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                # Select or move piece based on current game state
                if not game.select(row, col):
                    # If select returns False, handle the invalid selection
                    game.selected = None  # Reset selected piece

        # Update the display
        game.update()

    pygame.quit()  # Exit the game cleanly

if __name__ == "__main__":
    main()  # Call the main function to start the game
