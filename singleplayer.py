import pygame
from common import *
import chess
import chess.pgn

class DifficultyMenu:
    def __init__(self):
        self.options = ["Easy", "Medium", "Hard", "Fales", "Exit"]
        self.selected_option = 0
        self.font_title = pygame.font.Font(None, 64)
        self.font_option = pygame.font.Font(None, 50)
        self.shadow_color = (128, 119, 97)
        self.highlight_color = (187, 250, 245)
        self.font_color = (130, 179, 175)
        self.background_color = (222, 210, 177)

    def draw(self, screen: pygame.Surface):
        screen.fill(self.background_color)

        title_surface = self.font_title.render("Select Difficulty", True, self.font_color)
        title_shadow = self.font_title.render("Select Difficulty", True, self.shadow_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_shadow, title_rect.move(3, 3))
        screen.blit(title_surface, title_rect)

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

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "exit"  # Vrátí se k ukončení
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.selected_option
                elif event.key == pygame.K_ESCAPE:  # Stisknutí ESC
                    return "back"  # Návrat do hlavního menu
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    for index in range(len(self.options)):
                        option_rect = self.font_option.render(self.options[index], True, self.font_color).get_rect(center=(WIDTH // 2, HEIGHT // 2 + index * 60))
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            return index
        return None

def selecting_difficulty(screen: pygame.Surface):
    menu = DifficultyMenu()
    run = True
    while run:
        events = pygame.event.get()
        menu_result = menu.handle_input(events)
        if menu_result is not None:
            if menu_result == "back":  # Návrat do hlavního menu
                return None
            elif menu_result == "exit":  # Ukončení programu
                return "exit"
            # Opraveno, aby se zabránilo IndexError
            if 0 <= menu_result < len(menu.options) - 1:  # Poslední volba je "Exit"
                return ["easy", "medium", "hard", "Fales"][menu_result]
            else:
                return None  # Vrátí None, pokud se vybere "Exit"

        menu.draw(screen)
        pygame.display.update()

def main(debug=False):
    global logger
    screen, board, logger, clock, images, font = init_game(debug)

    pygame.display.set_caption("Chess - Single Player")

    while True:
        selected_difficulty = selecting_difficulty(screen)
        if selected_difficulty is None:  # Pokud se vrátíme do hlavního menu
            return  # Návrat do hlavního menu
        if selected_difficulty == "exit":  # Pokud se ukončuje program
            break  # Ukončení smyčky hry a návrat do hlavního menu

        logger.debug("Entering game loop")

        game = Game(screen, board, images, font)
        game.players["black"] = AI(chess.BLACK, selected_difficulty)

        run = True
        while run:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:  # Pokud se zavře okno
                    run = False  # Ukončete smyčku hry
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # Pokud stisknete ESC
                    run = False  # Ukončete smyčku hry

            game.loop(events)
            pygame.display.update()  # Aktualizace obrazovky
            clock.tick(60)

    pygame.quit()  # Ukončení Pygame po návratu do hlavního menu

if __name__ == "__main__":
    try:
        debug = input("Enable debug mode? (y/n): ").strip().lower()
        debug = True if debug == "y" else False
        main(debug)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
