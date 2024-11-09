import pygame
from common import *

def main(debug=False):
    global logger
    screen, board, logger, clock, images = init_game(debug, __name__)

    pygame.display.set_caption("Czess - local multiplayer")

    game = Game(screen, board, images)

    logger.debug("Entering game loop")
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
    