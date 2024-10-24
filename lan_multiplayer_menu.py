import pygame
import sys
from common import *  # Assuming common.py contains necessary classes

class LanMenu:
    def __init__(self):
        # Inicializace možností obtížnosti a nápověd
        self.options = ["Host", "Connect", "Return"]
        self.help_texts = [
            "Host a server for your friend",  # Popis pro Easy
            "Connect to your friend.",  # Popis pro Medium
            "Go back to the main menu."  # Popis pro Return
        ]
        self.selected_option = 0  # Index aktuálně vybrané možnosti
        # Nastavení fontů pro titulek a možnosti
        self.font_title = pygame.font.Font(None, 64)
        self.font_option = pygame.font.Font(None, 50)
        self.font_help = pygame.font.Font(None, 30)
        # Nastavení barev pro pozadí, text a možnosti
        self.shadow_color = (128, 119, 97)
        self.highlight_color = (187, 250, 245)
        self.font_color = (130, 179, 175)
        self.background_color = (222, 210, 177)  # Barva pozadí

    def draw(self, screen: pygame.Surface):
        # Vyplnění obrazovky barvou pozadí
        screen.fill(self.background_color)

        # Renderování titulku
        title_surface = self.font_title.render("LAN Multiplayer:", True, self.font_color)
        title_shadow = self.font_title.render("LAN Multiplayer:", True, self.shadow_color)
        title_rect = title_surface.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 4))
        screen.blit(title_shadow, title_rect.move(3, 3))  # Vytvoření stínu titulku
        screen.blit(title_surface, title_rect)

        # Posun nápovědy dolů, aby se nezasahovalo do položky "Return"
        help_color = self.font_color  # Výchozí barva pro nápovědu

        help_surface = self.font_help.render(self.help_texts[self.selected_option], True, help_color)
        help_rect = help_surface.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 1.07))
        screen.blit(help_surface, help_rect)

        option_height = MENU_HEIGHT // (len(self.options) + 1)
        spacing = option_height * 0.5  # Nastavení mezery mezi možnostmi

        for index, option in enumerate(self.options):
            color = self.highlight_color if index == self.selected_option else self.font_color  # Zvýraznění Return

            # Renderování možnosti s efektem stínu
            option_surface = self.font_option.render(option, True, color)
            option_shadow = self.font_option.render(option, True, self.shadow_color)
            option_rect = option_surface.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + index * spacing))

            # Upravujeme pozici pro Return
            if option == "Return":
                option_rect.y += 20  # Posunout Return o 20 pixelů níže

            # Zobrazení textu na obrazovce
            screen.blit(option_shadow, option_rect.move(3, 3))
            screen.blit(option_surface, option_rect)

    def move_selection(self, direction):
        # Posunutí vybrané možnosti
        self.selected_option = (self.selected_option + direction) % len(self.options)

    def handle_input(self, events: tuple[pygame.event.Event, ...]):
        for event in events:
            if event.type == pygame.QUIT:
                log.info("Exiting")  # Logování události ukončení
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.move_selection(-1)  # Posun nahoru
                elif event.key == pygame.K_DOWN:
                    self.move_selection(1)  # Posun dolů
                elif event.key == pygame.K_RETURN:
                    return self.selected_option  # Potvrzení výběru
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                for index in range(len(self.options)):
                    if self.options[index] == "Return":
                        option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(MENU_WIDTH // 2, (MENU_HEIGHT // 2 + index * (MENU_HEIGHT // (len(self.options) + 1)) * 0.5)+20))
                    else:
                        option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + index * (MENU_HEIGHT // (len(self.options) + 1)) * 0.5))
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_option = index  # Nastavení vybrané možnosti na základě pohybu myši
                        break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Levé tlačítko myši
                    mouse_x, mouse_y = event.pos
                    for index in range(len(self.options)):
                        if self.options[index] == "Return":
                            option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(MENU_WIDTH // 2, (MENU_HEIGHT // 2 + index * (MENU_HEIGHT // (len(self.options) + 1)) * 0.5)+20))
                        else:
                            option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + index * (MENU_HEIGHT // (len(self.options) + 1)) * 0.5))
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_option = index  # Nastavení vybrané možnosti na základě kliknutí
                            return self.selected_option
        return None  # Pokud nebyla provedena žádná akce
    

def main(debug=False):
    global logger
    _, _, logger, _, _ = init_game(debug, __name__)
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))

    pygame.display.set_caption("Czess - LAN multiplayer")

    menu = LanMenu()

    logger.debug("Entering main loop")
    run = True
    while run:
        events = pygame.event.get()  # Získání událostí
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")  # Logování události ukončení
                run = False
                pygame.quit()  # Ukončení Pygame
                return
        # Zpracování vstupů a vykreslení menu
        menu_result = menu.handle_input(events)
        if menu_result is not None:
            # Logování výběru obtížnosti
            if menu_result == 0:
                logger.info("Starting server")            
                import lan_multiplayer_server as server
                server.main(debug)
            elif menu_result == 1:
                logger.info("Starting game with medium difficulty")
                import lan_multiplayer_client as client
                client.main(debug)
            elif menu_result == 2:  # Return
                import main  # Importujeme main.py pro návrat
                main.main()  # Voláme hlavní funkci v main.py
            run = False  # Ukončíme aktuální smyčku

        if run:
            menu.draw(screen)  # Vykreslení menu
            pygame.display.update()  # Aktualizace obrazovky

if __name__ == "__main__":
    try:
        debug = input("Enable debug mode? (y/n): ").strip().lower()
        debug = True if debug == "y" else False
        main(debug)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e