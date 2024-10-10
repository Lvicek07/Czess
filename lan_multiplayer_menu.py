import pygame
import sys
from common import *  # Assuming common.py contains necessary classes
import logging as log
from os import chdir, mkdir
from os.path import abspath, dirname
from os.path import isdir
from datetime import datetime

class LanMenu:
    def __init__(self):
        self.options = ["Host", "Connect", "Watch"]
        self.selected_option = 0
        self.font = pygame.font.Font(None, 42)

    def draw(self, screen):
        screen.fill(WHITE)  # Fill the background with white
        title_surface = self.font.render("LAN multiplayer", True, FONT_COLOR)
        help_surface = self.font.render("Use arrow keys to select", True, FONT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surface, title_rect)
        help_rect = help_surface.get_rect(center=(WIDTH // 2, HEIGHT // 1.2))
        screen.blit(help_surface, help_rect)

        for index, option in enumerate(self.options):
            color = FONT_COLOR if index == self.selected_option else (100, 100, 100)
            option_surface = self.font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + index * 40))
            screen.blit(option_surface, option_rect)

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.selected_option  # Return selected option
        return None  # No option selected
    

def main(current_date):
    global logger
    chdir(dirname(abspath(__file__)))
    if not isdir('logs'):
        mkdir("logs")
    logger = log.getLogger(__name__)
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    pygame.init()

    logger.debug("Initializing main menu")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess Game')

    menu = LanMenu()

    logger.debug("Entering main loop")
    run = True
    while run:
        events = pygame.event.get()
        menu_result = menu.handle_input(events)
        
        if menu_result is not None:
            if menu_result == 0:  # Singleplayer
                logger.info("Starting server")

                import lan_multiplayer_server as server
                server.main(current_date)
                run = False
            elif menu_result == 1:  # Local Multiplayer
                logger.info("Starting local multiplayer session")

                import lan_multiplayer_client as client
                client.main(current_date)
                run = False
            elif menu_result == 2:  # LAN Multiplayer
                logger.info("Starting LAN multiplayer session")

                import lan_multiplayer_watcher as watcher
                watcher.main(current_date)
                run = False

        menu.draw(screen)
        pygame.display.flip()  # Update the display

if __name__ == "__main__":
    try:
        current_date = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        main(current_date)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
