import socket
import pygame
from common import *
import chess
import chess.pgn
from datetime import datetime
import pickle
import pygame_textinput

# Server details
PORT = 65432
BUFFER_SIZE = 1024

def connect_to_server(server_ip: str):
    """Connects to the chess server."""
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_ip, PORT))
    print(f"Connected to the server at {server_ip}:{PORT}")
    return conn

def main(current_date):
    global logger
    screen, board, logger, clock, images, game, node, font = init_game(current_date)

    pygame.display.set_caption("Chess - LAN multiplayer - client")

    player_black = Player(chess.BLACK)
    player_none = Player(chess.WHITE)

    moves = list()
    last_move = None
    run = True
    game_end = False

    # Connect to the server (Player 1)

    textinput = pygame_textinput.TextInputVisualizer(font_object=font)

    run = True
    while run:
        screen.fill(EGGSHELL)
        title_surface = font.render(f"Waiting for IP", True, FONT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surface, title_rect)
        title_surface = font.render(f"IP: ", True, FONT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2-150, HEIGHT // 2))
        screen.blit(title_surface, title_rect)

        events = pygame.event.get()
        mouse = pygame.mouse.get_pos() 
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Exiting")
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN: 
                if WIDTH/2+ 150 <= mouse[0] <= WIDTH/2+140+ 150 and HEIGHT/2-18 <= mouse[1] <= HEIGHT/2+22: 
                    SERVER_IP = textinput.value
                    run = False
        # Feed it with events every frame
        textinput.update(events)
        # Blit its surface onto the screen
        screen.blit(textinput.surface, (WIDTH // 2-130, HEIGHT // 2-15))

        if WIDTH/2+ 150 <= mouse[0] <= WIDTH/2+140+ 150 and HEIGHT/2-18 <= mouse[1] <= HEIGHT/2+22: 
            pygame.draw.rect(screen, (170,170,170), [WIDTH/2 + 150, HEIGHT/2-18, 140, 40]) 
            
        else: 
            pygame.draw.rect(screen, (100,100,100), [WIDTH/2 + 150, HEIGHT/2-18, 140, 40])

        text = font.render('Connect' , True , FONT_COLOR)
        screen.blit(text, text.get_rect(center=(WIDTH // 2 + 70 + 150, HEIGHT // 2))) 

        pygame.display.update()
        clock.tick(30)

    conn = connect_to_server(SERVER_IP)
    while True:
        msg = conn.recv(1024) 
        if msg.decode() == "sync":
            break
    conn.send(b"play")

    logger.debug("Entering game loop")
    
    run = True
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

            draw_board(board, screen, (player_none, player_black), images)  # Only player_black is active

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
