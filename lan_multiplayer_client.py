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

def ip_input(screen, font):
    textinput = pygame_textinput.TextInputVisualizer(font_object=font)
    clock = pygame.time.Clock()
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
    return SERVER_IP


def main(debug=False):
    global logger
    screen, board, logger, clock, images, font = init_game(debug)

    pygame.display.set_caption("Chess - LAN multiplayer - client")

    game = Game(screen, board, images, font)

    SERVER_IP = ip_input(screen, font)

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

        game.loop(events)

        if not game.game_end:
            if board.turn == chess.BLACK:
                data = pickle.dumps((board, game.moves))  # Serialize the board and moves
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
                        board, game.moves = pickle.loads(data)  # Deserialize the data
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
