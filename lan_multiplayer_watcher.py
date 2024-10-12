import socket
import pygame
from common import *
import logging as log
from os import chdir
from os.path import abspath, dirname
from datetime import datetime

# Server details
SERVER_IP = '127.0.0.1'  # Change this to the server's IP address if needed
PORT = 65432
BUFFER_SIZE = 1024

def connect_to_server():
    """Connects to the chess server."""
    watcher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    watcher_socket.connect((SERVER_IP, PORT))
    print(f"Connected to the server at {SERVER_IP}:{PORT}")
    return watcher_socket

def main(current_date):
    global logger
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    logger.debug("Initializing LAN multiplayer watcher")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = init_game()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('consolas', FONT_SIZE)
    piece_images = load_images()
    
    run = True
    game_end = False

    # Connect to the server (Player 1)
    watcher_socket = connect_to_server()

    logger.debug("Entering watcher loop")

    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False

        if not game_end:
            # Wait for moves from the server
            move_data = receive_move(watcher_socket)
            if move_data is not None:
                board.push(move_data)
                print(f"Received move: {move_data}")

                if board.outcome() is not None:
                    print("Game ended: ", board.outcome())
                    game_end = True

            draw_board(board, screen, (None, None), piece_images)  # No players are active

        screen.blit(font.render(f"Spectator Mode", True, FONT_COLOR), (610, 0))
        pygame.display.update()  # Update the display
        clock.tick(60)

    # Close the connection when the game is over
    watcher_socket.close()

def receive_move(watcher_socket):
    """Receives the move from the server."""
    data = watcher_socket.recv(BUFFER_SIZE).decode()
    if data:
        return chess.Move.from_uci(data)
    return None

if __name__ == "__main__":
    try:
        current_date = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        main(current_date)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
