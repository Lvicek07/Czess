import pygame
from common import *
import chess
import chess.pgn
from datetime import datetime

def draw_menu(screen: pygame.Surface):
    screen.fill((30, 30, 30))  # Dark background
    font = pygame.font.Font(None, 74)
    title_text = font.render("Select Difficulty", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 4, HEIGHT // 4))

    button_font = pygame.font.Font(None, 48)
    difficulties = ["Easy", "Medium", "Hard", "Fales"]
    for i, difficulty in enumerate(difficulties):
        button_text = button_font.render(difficulty, True, (255, 255, 255))
        screen.blit(button_text, (WIDTH // 4, HEIGHT // 2 + i * 60))

    pygame.display.flip()

def main(current_date):
    global logger
    screen, board, logger, clock, images, game, node, font = init_game(current_date)

    pygame.display.set_caption("Chess - single player")

    selected_difficulty = None
    while selected_difficulty is None:
        draw_menu(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                y = mouse_pos[1]
                if HEIGHT // 2 < y < HEIGHT // 2 + 240:  # Checking button area
                    index = (y - (HEIGHT // 2)) // 60
                    if 0 <= index < 4:
                        selected_difficulty = ["easy", "medium", "hard", "Fales"][index]

    player_white = Player(chess.WHITE, board)
    ai_black = AI(chess.BLACK, selected_difficulty)

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
                game_state = "On turn: White"
                player_white.on_move(board, events)
            else:
                game_state = "On turn: Black"
                ai_black.on_move(board)
                
            
            draw_board(board, screen, (player_white, ai_black), images)

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