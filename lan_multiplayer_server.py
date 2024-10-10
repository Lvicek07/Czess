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
SERVER_IP = '0.0.0.0'  # Listening on all interfaces
PORT = 65432
BUFFER_SIZE = 1024

def start_server():
    """Sets up the server and waits for Player 2 to connect."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, PORT))
    server_socket.listen(1)
    print(f"Server started, waiting for Player 2 to connect at {SERVER_IP}:{PORT}...")

    conn, addr = server_socket.accept()
    print(f"Player 2 connected from {addr}")
    return conn

def send_move(conn, move):
    """Sends the move over the network to Player 2."""
    conn.sendall(move.encode())

def receive_move(conn):
    """Receives the move from Player 2."""
    data = conn.recv(BUFFER_SIZE).decode()
    return chess.Move.from_uci(data)

def main(current_date):
    global logger
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    logger.debug("Initializing LAN multiplayer server")
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

    # Start the server and wait for Player 2 to connect
    conn = start_server()

    logger.debug("Entering game loop")

    while run:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                run = False

        if not game_end:
            if board.turn == chess.WHITE:
                # Player 1 (server/white) makes a move
                player_white.on_move(board, events)
                if player_white.selected_piece is None:  # Move made
                    move = board.peek().uci()
                    send_move(conn, move)  # Send the move to Player 2
                    print(f"Player 1 (White) moved: {move}")

            else:
                # Player 2 (client/black) makes a move
                print("Waiting for Player 2 (Black) to move...")
                move = receive_move(conn)  # Receive the move from Player 2
                if move in board.legal_moves:
                    board.push(move)
                    print(f"Player 2 (Black) moved: {move}")
                else:
                    print("Received an invalid move from Player 2.")

            draw_board(board, screen, (player_white, player_black), piece_images)

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
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        main(current_date)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e
