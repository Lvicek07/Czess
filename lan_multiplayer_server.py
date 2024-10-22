import socket
import pygame
from common import *
import chess
import chess.pgn
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

def wait_for_connection(screen: pygame.Surface, server_socket: socket.socket):
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
        title_surface = FONT.render(f"Server started, waiting for Player 2", True, FONT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surface, title_rect)
        title_surface = FONT.render(f"IP: {get_ip_address()}", True, FONT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 1.2))
        screen.blit(title_surface, title_rect)
        pygame.display.flip()

    screen.fill(WHITE)
    title_surface = FONT.render(f"Player 2 connected from {addr}", True, FONT_COLOR)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_surface, title_rect)
    pygame.display.flip()
    return conn


def main(debug=False):
    global logger
    screen, board, logger, clock, images = init_game(debug)

    pygame.display.set_caption("Chess - LAN multiplayer - server")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, PORT))
    server_socket.listen(1)
    server_socket.settimeout(0.25)  # Set timeout of 1 second

    conn = wait_for_connection(screen, server_socket)

    logger.debug("Entering game loop")

    game = Game(screen, board, images)

    run = True
    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False

        game.loop(events, multiplayer="server")

        if not game.game_end:
            if game.board.turn == chess.WHITE:
                data = pickle.dumps((game.board, game.moves))  # Serialize the board and moves
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
                        game.board, game.moves = pickle.loads(data)  # Deserialize the data
                except ValueError:
                    pass

        pygame.display.update()  # Update the display
        clock.tick(60)

    # Close the connection when the game is over
    conn.close()


if __name__ == "__main__":
    try:
        debug = input("Enable debug mode? (y/n): ").strip().lower()
        debug = True if debug == "y" else False
        main(debug)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
