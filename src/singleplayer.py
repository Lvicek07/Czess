import pygame
import logging as log
from common import *

class DifficultyMenu:
    def __init__(self):
        # Inicializace možností obtížnosti a nápověd
        self.options = ["Easy", "Medium", "Hard", "Fales", "Return"]
        self.help_texts = [
            "AI does random moves..",  # Popis pro Easy
            "AI tries to hold middle squares.",  # Popis pro Medium
            "AI is aggressive.",  # Popis pro Hard
            "You can pray for Fales's mercy.",  # Popis pro Fales
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
        self.easy_color = (51, 204, 51)  # Zelená pro Easy
        self.medium_color = (227, 148, 39)  # Oranžová pro Medium
        self.hard_color = (217, 46, 68)  # Červená pro Hard
        self.fales_color = (149, 56, 161)  # Fialová pro Fales
        self.background_color = (222, 210, 177)  # Barva pozadí

    def draw(self, screen: pygame.Surface, width: int, height: int):
        # Vyplnění obrazovky barvou pozadí
        screen.fill(self.background_color)

        # Renderování titulku
        title_surface = self.font_title.render("Select Difficulty:", True, self.font_color)
        title_shadow = self.font_title.render("Select Difficulty:", True, self.shadow_color)
        title_rect = title_surface.get_rect(center=(width // 2, height // 4))
        screen.blit(title_shadow, title_rect.move(3, 3))  # Vytvoření stínu titulku
        screen.blit(title_surface, title_rect)

        # Posun nápovědy dolů, aby se nezasahovalo do položky "Return"
        help_color = self.font_color  # Výchozí barva pro nápovědu
        if self.options[self.selected_option] == "Fales":
            help_color = self.fales_color  # Fialová barva pro popisek Fales
        elif self.options[self.selected_option] == "Easy":
            help_color = self.easy_color  # Zelená barva pro popisek Easy
        elif self.options[self.selected_option] == "Medium":
            help_color = self.medium_color  # Oranžová barva pro popisek Medium
        elif self.options[self.selected_option] == "Hard":
            help_color = self.hard_color  # Červená barva pro popisek Hard

        help_surface = self.font_help.render(self.help_texts[self.selected_option], True, help_color)
        help_rect = help_surface.get_rect(center=(width // 2, height // 1.07))
        screen.blit(help_surface, help_rect)

        option_height = height // (len(self.options) + 1)
        spacing = option_height * 0.5  # Nastavení mezery mezi možnostmi

        for index, option in enumerate(self.options):
            # Nastavení barvy podle vybrané možnosti
            if option == "Easy":
                color = self.easy_color if index == self.selected_option else self.font_color
            elif option == "Medium":
                color = self.medium_color if index == self.selected_option else self.font_color
            elif option == "Hard":
                color = self.hard_color if index == self.selected_option else self.font_color
            elif option == "Fales":
                color = self.fales_color if index == self.selected_option else self.font_color
            elif option == "Return":
                color = self.highlight_color if index == self.selected_option else self.font_color  # Zvýraznění Return
            else:
                color = self.font_color  # Výchozí barva

            # Renderování možnosti s efektem stínu
            option_surface = self.font_option.render(option, True, color)
            option_shadow = self.font_option.render(option, True, self.shadow_color)
            option_rect = option_surface.get_rect(center=(width // 2, height // 2 + index * spacing))

            # Upravujeme pozici pro Return
            if option == "Return":
                option_rect.y += 20  # Posunout Return o 20 pixelů níže

            # Zobrazení textu na obrazovce
            screen.blit(option_shadow, option_rect.move(3, 3))
            screen.blit(option_surface, option_rect)

    def move_selection(self, direction):
        # Posunutí vybrané možnosti
        self.selected_option = (self.selected_option + direction) % len(self.options)

    def handle_input(self, events: tuple[pygame.event.Event, ...], width: int, height: int):
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
                        option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(width // 2, (height // 2 + index * (height // (len(self.options) + 1)) * 0.5)+20))
                    else:
                        option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(width // 2, height // 2 + index * (height // (len(self.options) + 1)) * 0.5))
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_option = index  # Nastavení vybrané možnosti na základě pohybu myši
                        break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Levé tlačítko myši
                    mouse_x, mouse_y = event.pos
                    for index in range(len(self.options)):
                        if self.options[index] == "Return":
                            option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(width // 2, (height // 2 + index * (height // (len(self.options) + 1)) * 0.5)+20))
                        else:
                            option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(width // 2, height // 2 + index * (height // (len(self.options) + 1)) * 0.5))
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_option = index  # Nastavení vybrané možnosti na základě kliknutí
                            return self.selected_option
        return None  # Pokud nebyla provedena žádná akce

def main(debug=False):
    global logger
    screen, board, logger, clock, images = init_game(debug, __name__)

    logger.debug("Initializing difficulty menu")
    
    # Nastavení okna Pygame
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption('Czess - Difficulty Selection')  # Titulek okna

    menu = DifficultyMenu()  # Vytvoření instance menu

    logger.debug("Entering difficulty selection loop")
    run = True
    while run:
        events = pygame.event.get()  # Získání událostí
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")  # Logování události ukončení
                run = False
                pygame.quit()  # Ukončení Pygame
                return

        # Zajištění minimální velikosti okna
        width, height = screen.get_size()
        if width < 800 or height < 600:
            width = max(width, 800)
            height = max(height, 600)
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Zpracování vstupů a vykreslení menu
        menu_result = menu.handle_input(events, width, height)
        if menu_result is not None:
            # Logování výběru obtížnosti
            if menu_result == 0:
                logger.info("Starting game with easy difficulty")            
                selected_difficulty = "easy"
            elif menu_result == 1:
                logger.info("Starting game with medium difficulty")
                selected_difficulty = "medium"
            elif menu_result == 2:
                logger.info("Starting game with hard difficulty")
                selected_difficulty = "hard"
            elif menu_result == 3:
                logger.info("Starting game with Fales difficulty")
                selected_difficulty = "Fales"
            elif menu_result == 4:  # Return
                import main  # Importujeme main.py pro návrat
                main.main()  # Voláme hlavní funkci v main.py
            run = False  # Ukončíme aktuální smyčku

        if run:
            menu.draw(screen, width, height)  # Vykreslení menu
            pygame.display.update()  # Aktualizace obrazovky
    run = True
    while run:
        logger.debug("Entering game loop")
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # Vytvoření nové hry s vybranou obtížností pro AI
        game = Game(screen, board, images)
        game.players["black"] = AI(chess.BLACK, selected_difficulty)
        run = True
        # Hlavní smyčka hry
        while run:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    run = False  # Ukončení hry, pokud je okno zavřeno
                    pygame.quit()
                    return  # Ukončení celého programu
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    run = False  # Ukončení aktuální hry, návrat do menu obtížností
            game.loop(events)  # Hlavní herní smyčka
            pygame.display.update()
            clock.tick(60)

    pygame.quit()  # Ukončení Pygame
    

if __name__ == "__main__":  # Kontrola spuštění skriptu
    try:
        debug = input("Enable debug mode? (y/n): ").strip().lower()
        debug = True if debug == "y" else False
        main(debug)  # Spuštění hlavní funkce
        logger.info("Program exited")  # Logování ukončení
    except KeyboardInterrupt:
        logger.info("User Exited")  # Logování přerušení uživatelem
    except Exception as e:
        logger.error(e)  # Logování chyb
        raise e  # Vyhození chyby

