import pygame
import logging as log
from os import chdir
from os.path import abspath, dirname
from common import *

class MainMenu:
    def __init__(self):
        self.options = ["Singleplayer", "Local Multiplayer", "LAN Multiplayer", "Exit"]
        self.help_texts = [
            "Play against the AI.",
            "Play with a friend on the same device.",
            "Play with a friend over the network.",
            "Exit the game."
        ]
        self.selected_option = 0
        self.font_title = pygame.font.Font(None, 64)
        self.font_option = pygame.font.Font(None, 50)
        self.font_help = pygame.font.Font(None, 30)
        self.shadow_color = (128, 119, 97)
        self.highlight_color = (187, 250, 245)
        self.font_color = (130, 179, 175)
        self.exit_color = (255, 0, 0)  # Červená barva pro Exit
        self.background_color = (222, 210, 177)

    def draw(self, screen: pygame.Surface, width: int, height: int):
        screen.fill(self.background_color)

        title_surface = self.font_title.render("CZESS", True, self.font_color)
        title_shadow = self.font_title.render("CZESS", True, self.shadow_color)
        title_rect = title_surface.get_rect(center=(width // 2, height // 4))
        screen.blit(title_shadow, title_rect.move(3, 3))
        screen.blit(title_surface, title_rect)

        # Posun nápovědy dolů, aby se nezasahovalo do položky "Exit"
        help_surface = self.font_help.render(self.help_texts[self.selected_option], True, self.font_color)
        help_rect = help_surface.get_rect(center=(width // 2, height // 1.1))
        screen.blit(help_surface, help_rect)

        # Dynamicky upravujeme pozice a velikosti textu na základě velikosti okna
        option_height = height // (len(self.options) + 1)
        spacing = option_height * 0.5  # Vzdálenost mezi položkami na základě výšky okna

        for index, option in enumerate(self.options):
            if index == self.selected_option:
                color = self.exit_color if option == "Exit" else self.highlight_color
            else:
                color = self.font_color
            
            option_surface = self.font_option.render(option, True, color)
            option_shadow = self.font_option.render(option, True, self.shadow_color)
            option_rect = option_surface.get_rect(center=(width // 2, height // 2 + index * spacing))

            # Upravujeme pozici pro Exit
            if option == "Exit":
                option_rect.y += 20  # Posunout Exit o 20 pixelů níže

            screen.blit(option_shadow, option_rect.move(3, 3))
            screen.blit(option_surface, option_rect)

    def move_selection(self, direction):
        self.selected_option = (self.selected_option + direction) % len(self.options)

    def handle_input(self, events, width, height):
        # Dynamicky upravujeme pozici a velikosti textu na základě velikosti okna
        option_height = height // (len(self.options) + 1)
        spacing = option_height * 0.5  # Vzdálenost mezi položkami na základě výšky okna

        for event in events:
            if event.type == pygame.QUIT:
                log.info("Exiting")
                return "exit"  # Návrat pro ukončení
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.move_selection(-1)
                elif event.key == pygame.K_DOWN:
                    self.move_selection(1)
                elif event.key == pygame.K_RETURN:
                    return self.selected_option
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                for index in range(len(self.options)):
                    option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(width // 2, height // 2 + index * spacing))
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_option = index
                        break  # Ujistíme se, že se zvýraznění změní jen na jednu položku
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    for index in range(len(self.options)):
                        option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(width // 2, height // 2 + index * spacing))
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_option = index
                            return self.selected_option
        return None

def main(debug=False):
    global logger
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    if debug:
        log.basicConfig(level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
    else:
        log.basicConfig(level=log.WARNING, format='%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')

    pygame.init()

    logger.debug("Initializing main menu")
    
    # Nastavení výchozí velikosti okna
    initial_width, initial_height = 800, 600
    screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)  # Povolíme změnu velikosti okna
    pygame.display.set_caption('Chess Game')

    menu = MainMenu()

    logger.debug("Entering main loop")
    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False
                pygame.quit()  # Ukončí Pygame a tím pádem i kreslení
                return  # Návrat, aby se předešlo dalšímu vykreslování

        # Kontrola velikosti okna a nastavení minimální velikosti
        width, height = screen.get_size()
        if width < 800 or height < 600:
            width = max(width, 800)
            height = max(height, 600)
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        menu_result = menu.handle_input(events, width, height)  # Předat šířku a výšku do handle_input
        if menu_result is not None:
            if menu_result == 0:
                logger.info("Starting singleplayer session")            
                import singleplayer
                singleplayer.main(debug)
                run = False
            elif menu_result == 1:
                logger.info("Starting local multiplayer session")
                import local_multiplayer
                local_multiplayer.main(debug)
                run = False
            elif menu_result == 2:
                logger.info("Starting LAN multiplayer session")                
                import lan_multiplayer_menu
                lan_multiplayer_menu.main(debug)
                run = False
            elif menu_result == 3:
                logger.info("Exiting the program")
                run = False  # Ukončí smyčku pro návrat do hlavního menu

        if run:  # Zkontroluj, zda stále pokračujeme
            menu.draw(screen, width, height)  # Předat velikost obrazovky do metody draw
            pygame.display.update()

    pygame.quit()  # Ukončení Pygame po návratu do hlavního menu


if __name__ == "__main__":
    try:
        debug = input("Enable debug mode? (y/n): ").strip().lower()
        debug = True if debug == "y" else False
        main(debug)
        logger.info("Program exited")
    except KeyboardInterrupt:
        logger.info("User Exited")
    except Exception as e:
        logger.error(e)
        raise e