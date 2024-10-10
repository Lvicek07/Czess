"""
Vždy použij tuto předlohu pro výtvor kokotit
"""

import pygame
from common import *
import logging as log
import chess
from os import chdir
from os.path import abspath, dirname
from datetime import datetime

def main(current_date):
    global logger
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    clock = pygame.time.Clock()

    """
    Init
    """

    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False

        """
        Logika
        """
        pygame.display.update()  # Update the display
        clock.tick(60)

if __name__ == "__main__":
    try:
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        main(current_date)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
