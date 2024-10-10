import pygame
from common import *
import logging as log
import chess
import chess.pgn
from os import chdir
from os.path import abspath, dirname
from datetime import datetime

def main(current_date):
    global logger
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    logger.debug("Initializing local multiplayer app")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = init_game()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('consolas', FONT_SIZE)
    piece_images = load_images()
    game = chess.pgn.Game()
    node = game

    player_white = Player(chess.WHITE, board)
    player_black = Player(chess.BLACK, board)

    moves = list()
    last_move = None
    run = True
    game_end = False

    logger.debug("Entering game loop")

    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False
        if not game_end:
            if board.turn == chess.WHITE:
                player_white.on_move(board, events)
                game_state = "On turn: White"
            else:
                player_black.on_move(board, events)
                game_state = "On turn: Black"
            
            draw_board(board, screen, (player_white, player_black), piece_images)

            if board.outcome() != None:
                print("Game ended: ", board.outcome())
                game_state = f"Game ended: {board.outcome()}"
                game_end = True
                with open(f"game_log_{current_date}.pgn", "w") as pgn_file:
                    exporter = chess.pgn.FileExporter(pgn_file)
                    game.accept(exporter)

        screen.blit(font.render(game_state, True, FONT_COLOR), (610,0))
        try:
            if board.peek() != last_move:
                last_move = board.peek()
                moves.append(last_move)
                print(type(node))
                node = node.add_variation(last_move)
            print_game_log(screen, font, moves)
        except IndexError:
            screen.blit(font.render("No moves", True, FONT_COLOR), (610,FONT_SIZE+5))

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