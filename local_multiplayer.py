import pygame
from common import *

def main(debug=False):
    global logger
    screen, board, logger, clock, images, font = init_game(debug)

    pygame.display.set_caption("Chess - local multiplayer")

    game = Game(screen, board, images, font)

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
        main(debug=True)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
    