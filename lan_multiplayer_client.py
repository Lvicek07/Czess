import socket
import pygame
from common import *
import logging as log
import chess
import chess.pgn
from os import chdir
from os.path import abspath, dirname
from datetime import datetime

# Server details
SERVER_IP = '127.0.0.1'  # Change this to the server's IP address if needed
PORT = 65432
BUFFER_SIZE = 1024

def connect_to_server():
    """Connects to the chess server."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    print(f"Connected to the server at {SERVER_IP}:{PORT}")
    return client_socket

def send_move(client_socket, move):
    """Sends the move over the network to Player 1."""
    client_socket.sendall(move.encode())

def main(current_date):
    global logger
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    logger.debug("Initializing LAN multiplayer client")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = init_game()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('consolas', FONT_SIZE)
    piece_images = load_images()
    game = chess.pgn.Game()
    node = game

    player_black = Player(chess.BLACK, board)

    moves = list()
    last_move = None
    run = True
    game_end = False

    # Connect to the server (Player 1)
    client_socket = connect_to_server()

    logger.debug("Entering game loop")

    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False

        if not game_end:
            if board.turn == chess.BLACK:
                # Player 2 (client/black) makes a move
                player_black.on_move(board, events)
                if player_black.selected_piece is None:  # Move made
                    move = board.peek().uci()
                    send_move(client_socket, move)  # Send the move to Player 1
                    print(f"Player 2 (Black) moved: {move}")

            # Player 1 (server/white) makes a move
            print("Waiting for Player 1 (White) to move...")
            move = receive_move(client_socket)  # Receive the move from Player 1
            if move in board.legal_moves:
                board.push(move)
                print(f"Player 1 (White) moved: {move}")
            else:
                print("Received an invalid move from Player 1.")

            draw_board(board, screen, (player_black, None), piece_images)  # Only player_black is active

            if board.outcome() is not None:
                print("Game ended: ", board.outcome())
                game_end = True
                with open(f"game_log_{current_date}.pgn", "w") as pgn_file:
                    exporter = chess.pgn.FileExporter(pgn_file)
                    game.accept(exporter)

        screen.blit(font.render(f"Turn: {'Black'}", True, FONT_COLOR), (610, 0))
        
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
    client_socket.close()

def receive_move(client_socket):
    """Receives the move from Player 1."""
    data = client_socket.recv(BUFFER_SIZE).decode()
    return chess.Move.from_uci(data)

if __name__ == "__main__":
    try:
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        main(current_date)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
