import pygame
from common import *
import chess
import chess.pgn

# Třída pro zobrazení a správu menu výběru obtížnosti
class DifficultyMenu:
    def __init__(self):
        # Definování jednotlivých možností obtížnosti
        self.options = ["Easy", "Medium", "Hard", "Fales", "Exit"]
        # Výchozí nastavení vybrané možnosti
        self.selected_option = 0
        # Inicializace fontů pro titul a možnosti
        self.font_title = pygame.font.Font(None, 64)
        self.font_option = pygame.font.Font(None, 50)
        # Definování barev pro stíny, zvýraznění a standardní text
        self.shadow_color = (128, 119, 97)
        self.highlight_color = (187, 250, 245)
        self.font_color = (130, 179, 175)
        self.background_color = (222, 210, 177)

    # Metoda pro vykreslení menu výběru obtížnosti
    def draw(self, screen: pygame.Surface):
        # Vyplnění pozadí
        screen.fill(self.background_color)

        # Vykreslení titulu menu s odstínem stínu
        title_surface = self.font_title.render("Select Difficulty", True, self.font_color)
        title_shadow = self.font_title.render("Select Difficulty", True, self.shadow_color)
        title_rect = title_surface.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 4))
        screen.blit(title_shadow, title_rect.move(3, 3))
        screen.blit(title_surface, title_rect)

        # Získání pozice myši
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Vykreslení jednotlivých možností obtížnosti
        for index, option in enumerate(self.options):
            # Zvýraznění vybrané možnosti
            if index == self.selected_option:
                color = self.highlight_color
            else:
                color = self.font_color

            # Vykreslení textu možnosti s odstínem stínu
            option_surface = self.font_option.render(option, True, color)
            option_shadow = self.font_option.render(option, True, self.shadow_color)
            option_rect = option_surface.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + index * 60))
            
            screen.blit(option_shadow, option_rect.move(3, 3))
            screen.blit(option_surface, option_rect)

    # Metoda pro pohyb mezi možnostmi
    def move_selection(self, direction):
        # Aktualizace vybrané možnosti pomocí cyklického pohybu
        self.selected_option = (self.selected_option + direction) % len(self.options)

    # Metoda pro zpracování uživatelského vstupu (klávesnice, myš)
    def handle_input(self, events):
        for event in events:
            # Uzavření aplikace, pokud je zavřeno okno
            if event.type == pygame.QUIT:
                return "exit"
            # Zpracování vstupů z klávesnice
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.move_selection(-1)  # Pohyb nahoru v seznamu možností
                elif event.key == pygame.K_DOWN:
                    self.move_selection(1)  # Pohyb dolů v seznamu možností
                elif event.key == pygame.K_RETURN:
                    return self.selected_option  # Potvrzení vybrané možnosti
                elif event.key == pygame.K_ESCAPE:
                    return "back"  # Návrat do předchozího menu
            # Zpracování pohybu myši
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                for index in range(len(self.options)):
                    option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + index * 60))
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_option = index  # Nastavení vybrané možnosti na základě pozice myši
            # Zpracování kliknutí myší
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Levé tlačítko myši
                    mouse_x, mouse_y = event.pos
                    for index in range(len(self.options)):
                        option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT // 2 + index * 60))
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_option = index  # Nastavení vybrané možnosti na základě kliknutí myši
                            return self.selected_option  # Potvrzení výběru
        return None

# Funkce pro zobrazení a zpracování menu výběru obtížnosti
def selecting_difficulty(screen: pygame.Surface):
    menu = DifficultyMenu()
    run = True
    while run:
        # Získání všech událostí (klávesnice, myš, zavření okna)
        events = pygame.event.get()
        menu_result = menu.handle_input(events)
        if menu_result is not None:
            # Pokud se uživatel rozhodne vrátit nebo ukončit hru
            if menu_result == "back":
                return None
            elif menu_result == "exit":
                return "exit"
            # Vrátí zvolenou obtížnost
            if 0 <= menu_result < len(menu.options) - 1:
                return ["easy", "medium", "hard", "Fales"][menu_result]
            else:
                return None

        # Vykreslení menu na obrazovku
        menu.draw(screen)
        pygame.display.update()

# Hlavní funkce hry
def main(debug=False):
    global logger
    # Inicializace hry (obrazovka, šachovnice, logger, časovač, obrázky, fonty)
    screen, board, logger, clock, images = init_game(debug)
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT), pygame.RESIZABLE)  # Povolíme změnu velikosti okna

    pygame.display.set_caption("Chess - Single Player")  # Nastavení názvu okna

    # Smyčka pro opakovaný výběr obtížnosti a následné hraní
    while True:
        selected_difficulty = selecting_difficulty(screen)  # Volba obtížnosti
        if selected_difficulty is None:
            return  # Pokud je výběr zrušen, ukončí se hra
        if selected_difficulty == "exit":
            break  # Pokud je zvoleno 'Exit', ukončí se hlavní smyčka

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
            pygame.display.update()  # Aktualizace obrazovky
            clock.tick(60)  # Nastavení FPS

        # Uvolnění paměti po skončení hry
        game = None

    pygame.quit()  # Ukončení pygame po skončení celé hry

# Spuštění programu
if __name__ == "__main__":
    try:
        # Aktivace debug režimu na základě uživatelského vstupu
        debug = input("Enable debug mode? (y/n): ").strip().lower()
        debug = True if debug == "y" else False
        main(debug)  # Spuštění hlavní funkce
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)  # Logování chyby
        raise e  # Opětovné vyvolání chyby
