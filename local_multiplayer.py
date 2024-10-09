import pygame
from common import *
import logging as log
import chess
from os import chdir
from os.path import abspath, dirname
from datetime import datetime

def main():
    global logger
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_filename = f"log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    logger.debug("Initializing local multiplayer app")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = init_game()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('consolas', 30)
    piece_images = load_images()

    player_white = Player(chess.WHITE, board)
    player_black = Player(chess.BLACK, board)

    logger.debug("Entering game loop")
    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False

        if board.turn == chess.WHITE:
            player_white.on_move(board, events)
            text = "On turn: white"
        else:
            player_black.on_move(board, events)
            text = "On turn: black"
        
        draw_board(board, screen, (player_white, player_black), piece_images)

        if board.outcome() != None:
            print("Game ended: ", board.outcome())
            run = False

        screen.blit(font.render(text, True, FONT_COLOR), (10,610))

        pygame.display.update()  # Update the display
        clock.tick(60)
        print(clock.get_fps())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(e)
        raise e