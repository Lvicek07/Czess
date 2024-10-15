import pygame
from common import *
import chess
import chess.pgn
from datetime import datetime

def main(current_date):
    global logger
    screen, board, logger, clock, images, game, node, font = init_game(current_date)

    pygame.display.set_caption("Chess - local multiplayer")

    player_white = Player(chess.WHITE)
    player_black = Player(chess.BLACK)

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
            
            draw_board(board, screen, (player_white, player_black), images)

            if board.outcome() != None:
                print("Game ended: ", board.outcome())
                game_state = f"Game ended: {board.outcome().result}"
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
        current_date = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        main(current_date)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
    