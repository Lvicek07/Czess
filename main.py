import pygame
import sys
from common import *
import logging as log
from os import chdir, mkdir
from os.path import abspath, dirname
from os.path import isdir
from datetime import datetime

class MainMenu:
    def __init__(self):
        self.options = ["Singleplayer", "Local Multiplayer", "LAN Multiplayer", "Exit"]
        self.selected_option = 0
        self.font_title = pygame.font.Font(None, 64)
        self.font_option = pygame.font.Font(None, 50)
        self.font_help = pygame.font.Font(None, 30)
        self.shadow_color = (100, 100, 100)
        self.highlight_color = (75, 37, 190)
        self.font_color = (0, 0, 0)
        self.background_color = (50, 50, 50)

    def draw(self, screen: pygame.Surface):
        screen.fill(self.background_color)

        title_surface = self.font_title.render("ŠLACH", True, self.font_color)
        title_shadow = self.font_title.render("ŠLACH", True, self.shadow_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_shadow, title_rect.move(3, 3))
        screen.blit(title_surface, title_rect)

        help_surface = self.font_help.render("Use arrow keys to select | Press Enter to choose | (also you can use mouse.. moron..)", True, self.font_color)
        help_rect = help_surface.get_rect(center=(WIDTH // 2, HEIGHT // 1.15))
        screen.blit(help_surface, help_rect)

        for index, option in enumerate(self.options):
            if index == self.selected_option:
                color = self.highlight_color
            else:
                color = self.font_color
            option_surface = self.font_option.render(option, True, color)
            option_shadow = self.font_option.render(option, True, self.shadow_color)
            option_rect = option_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + index * 60))

            screen.blit(option_shadow, option_rect.move(3, 3))
            screen.blit(option_surface, option_rect)

    def move_selection(self, direction):
        self.selected_option = (self.selected_option + direction) % len(self.options)

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
                    return self.selected_option
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    for index in range(len(self.options)):
                        option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(WIDTH // 2, HEIGHT // 2 + index * 60))
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_option = index
                            return self.selected_option
        return None

def main():
    global logger
    chdir(dirname(abspath(__file__)))
    if not isdir('logs'):
        mkdir("logs")
    logger = log.getLogger(__name__)
    current_date = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    pygame.init()

    logger.debug("Initializing main menu")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess Game')

    menu = MainMenu()

    logger.debug("Entering main loop")
    run = True
    while run:
        events = pygame.event.get()
        menu_result = menu.handle_input(events)
        if menu_result is not None:
            if menu_result == 0:
                logger.info("Starting singleplayer session")            
                import singleplayer
                singleplayer.main(current_date)
                run = False
            elif menu_result == 1:
                logger.info("Starting local multiplayer session")
                import local_multiplayer
                local_multiplayer.main(current_date)
                run = False
            elif menu_result == 2:
                logger.info("Starting LAN multiplayer session")                
                import lan_multiplayer_menu
                lan_multiplayer_menu.main(current_date)
                run = False
            elif menu_result == 3:
                logger.info("Exiting the program")
                run = False
        menu.draw(screen)
        pygame.display.update()

if __name__ == "__main__":
    try:
        main()
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
    