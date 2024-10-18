import pygame
from common import *
import chess
import chess.pgn

def draw_menu(screen: pygame.Surface):
    screen.fill((30, 30, 30))  # Dark background
    font = pygame.font.Font(None, 74)
    title_text = font.render("Select Difficulty", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 4, HEIGHT // 4))

    button_font = pygame.font.Font(None, 48)
    difficulties = ["Easy", "Medium", "Hard", "Fales"]
    for i, difficulty in enumerate(difficulties):
        button_text = button_font.render(difficulty, True, (255, 255, 255))
        screen.blit(button_text, (WIDTH // 4, HEIGHT // 2 + i * 60))

    pygame.display.flip()

def selecting_difficulty(screen: pygame.Surface):
    selected_difficulty = None
    while selected_difficulty is None:
        draw_menu(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                y = mouse_pos[1]
                if HEIGHT // 2 < y < HEIGHT // 2 + 240:  # Checking button area
                    index = (y - (HEIGHT // 2)) // 60
                    if 0 <= index < 4:
                        selected_difficulty = ["easy", "medium", "hard", "Fales"][index]
    return selected_difficulty

def main(debug=False):
    global logger
    screen, board, logger, clock, images, font = init_game(debug)

    pygame.display.set_caption("Chess - single player")

    selected_difficulty = selecting_difficulty(screen)

    logger.debug("Entering game loop")

    game = Game(screen, board, images, font)
    game.players["black"] = AI(chess.BLACK, selected_difficulty)

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False

        game.loop(events)
        pygame.display.update()  # Update the display
        clock.tick(60)


if __name__ == "__main__":
    try:
        debug = input("Enable debug mode? (y/n): ").strip().lower()
        debug = True if debug == "y" else False
        main(debug)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e