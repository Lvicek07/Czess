import pygame
import sys
from common import *  # Assuming common.py contains necessary classes

class LanMenu:
    def __init__(self):
        self.options = ["Host", "Connect"]
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
    

def main(debug=False):
    global logger
    screen, _, logger, _, _, _ = init_game(debug)

    pygame.display.set_caption("Czess - LAN multiplayer")

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
                server.main(debug)
                run = False
            elif menu_result == 1:  # Local Multiplayer
                logger.info("Starting local multiplayer session")

                import lan_multiplayer_client as client
                client.main(debug)
                run = False

        menu.draw(screen)
        pygame.display.flip()  # Update the display

if __name__ == "__main__":
    try:
        debug = input("Enable debug mode? (y/n): ").strip().lower()
        debug = True if debug == "y" else False
        main(debug)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e