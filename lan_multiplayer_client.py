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
PORT = 65432
BUFFER_SIZE = 1024

def connect_to_server(server_ip: str):
    """Connects to the chess server."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, PORT))
    print(f"Connected to the server at {server_ip}:{PORT}")
    return client_socket

def main(current_date):
    global logger
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    logger.debug("Initializing LAN multiplayer client")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess - LAN multiplayer - client")
    board = init_game()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('consolas', FONT_SIZE)
    piece_images = load_images()
    game = chess.pgn.Game()
    node = game

    player_black = Player(chess.BLACK, board)
    player_none = Player(chess.WHITE, board)

    moves = list()
    last_move = None
    run = True
    game_end = False

    # Connect to the server (Player 1)
    screen.fill(EGGSHELL)
    title_surface = font.render(f"Waiting for IP", True, FONT_COLOR)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_surface, title_rect)
    title_surface = font.render(f"Write the IP in console (10.1.1.0)", True, FONT_COLOR)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(title_surface, title_rect)
    title_surface = font.render(f"Windows might report this app as not responding, DO NOT CLOSE", True, FONT_COLOR)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 1.2))
    screen.blit(title_surface, title_rect)
    pygame.display.flip()

    SERVER_IP = input("IP: ")

    client_socket = connect_to_server(SERVER_IP)
    while True:
        msg = client_socket.recv(1024) 
        if msg.decode() == "sync":
            break
    client_socket.send(b"sync")

    logger.debug("Entering game loop")

    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False

        if not game_end:
            if board.turn == chess.BLACK:
                player_black.on_move(board, events)
                data = pickle.dumps((board, moves))  # Serialize the board and moves
                client_socket.send(data)  # Send serialized data
            else:
                try:
                    data = client_socket.recv(4096)  # Receive data
                    board, moves = pickle.loads(data)  # Deserialize the data
                except ValueError:
                    pass

            draw_board(board, screen, (player_none, player_black), piece_images)  # Only player_black is active

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
        clock.tick(25)

    # Close the connection when the game is over
    client_socket.close()

if __name__ == "__main__":
    try:
        current_date = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        main(current_date)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
