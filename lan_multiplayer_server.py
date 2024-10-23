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
    font_title       = pygame.font.Font(None, 64)
    font_option      = pygame.font.Font(None, 50)
    font_help        = pygame.font.Font(None, 30)
    shadow_color     = (128, 119, 97)
    highlight_color  = (187, 250, 245)
    font_color       = (130, 179, 175)
    background_color = (222, 210, 177)
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
        screen.fill(background_color)
        title_surface = font_title.render("Server started, waiting for Player 2", True, font_color)
        title_shadow = font_title.render("Server started, waiting for Player 2", True, shadow_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_shadow, title_rect.move(3, 3))
        screen.blit(title_surface, title_rect)
        title_surface = font_option.render(f"IP: {get_ip_address()}", True, font_color)
        title_shadow = font_option.render(f"IP: {get_ip_address()}", True, shadow_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 1.2))
        screen.blit(title_shadow, title_rect.move(3, 3))
        screen.blit(title_surface, title_rect)
        pygame.display.flip()

    screen.fill(WHITE)
    title_surface = font_help.render(f"Player 2 connected from {addr}", True, highlight_color)
    title_shadow = font_help.render(f"Player 2 connected from {addr}", True, shadow_color)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_shadow, title_rect.move(3, 3))
    screen.blit(title_surface, title_rect)
    pygame.display.flip()
    return conn


def main(debug=False):
    global logger
    screen, board, logger, clock, images = init_game(debug)

    pygame.display.set_caption("Czess - LAN multiplayer - server")

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
