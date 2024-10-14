import socket
import pygame
from common import *
import logging as log
import chess
import chess.pgn
from os import chdir
from os.path import abspath, dirname
from datetime import datetime
import pickle

# Server details

SERVER_IP = '0.0.0.0'  # Listening on all interfaces
PORT = 65432
BUFFER_SIZE = 1024

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def main(current_date):
    global logger
    screen, board, logger, clock, images, game, node, font = init_game(current_date)

    pygame.display.set_caption("Chess - LAN multiplayer - server")

    player_white = Player(chess.WHITE, board)
    player_black = Player(chess.BLACK, board)

    moves = list()
    last_move = None
    game_end = False

    # Start the server and wait for Player 2 to connect
    """Sets up the server and waits for Player 2 to connect."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, PORT))
    server_socket.listen(1)
    server_socket.settimeout(0.25)  # Set timeout of 1 second

    print(f"IP: {get_ip_address()}")

    run = True
    while run:
        try:
            conn, addr = server_socket.accept()
            conn.send(b"sync")
            while True:
                msg = conn.recv(1024) 
                if msg.decode() == "play":
                    break
            run = False
        except socket.timeout:
            pass  # Ignore the timeout and continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                raise SystemExit
        screen.fill(WHITE)
        title_surface = font.render(f"Server started, waiting for Player 2", True, FONT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surface, title_rect)
        title_surface = font.render(f"IP: {get_ip_address()}", True, FONT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 1.2))
        screen.blit(title_surface, title_rect)
        pygame.display.flip()

    screen.fill(WHITE)
    title_surface = font.render(f"Player 2 connected from {addr}", True, FONT_COLOR)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_surface, title_rect)
    pygame.display.flip()

    logger.debug("Entering game loop")

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False

        if not game_end:
            if board.turn == chess.WHITE:
                player_white.on_move(board, events)
                data = pickle.dumps((board, moves))  # Serialize the board and moves
                try:
                    conn.send(data)  # Send serialized data
                except [ConnectionResetError, ConnectionAbortedError]:
                    logger.info("Exiting")
                    run = False
            else:
                try:
                    data = conn.recv(4096)  # Receive data
                    if not data:
                        logger.error("Received empty data")
                        logger.info("Exiting")
                        run = False
                    else:
                        board , moves = pickle.loads(data)  # Deserialize the data
                except ValueError:
                    pass

            draw_board(board, screen, (player_white, player_black), images)

            if board.outcome() is not None:
                print("Game ended: ", board.outcome())
                game_end = True
                with open(f"game_log_{current_date}.pgn", "w") as pgn_file:
                    exporter = chess.pgn.FileExporter(pgn_file)
                    game.accept(exporter)

        screen.blit(font.render(f"Turn: {'White' if board.turn == chess.WHITE else 'Black'}", True, FONT_COLOR), (610, 0))
        
        try:
            if board.peek() != last_move:
                last_move = board.peek()
                moves.append(last_move)
                node = node.add_variation(last_move)
            print_game_log(screen, font, moves)
        except IndexError:
            screen.blit(font.render("No moves", True, FONT_COLOR), (610, FONT_SIZE + 5))

        pygame.display.update()  # Update the display
        clock.tick(60)

    # Close the connection when the game is over
    conn.close()


if __name__ == "__main__":
    try:
        current_date = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        main(current_date)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
