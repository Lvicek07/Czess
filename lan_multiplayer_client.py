import socket
import pygame
from common import *
import chess
import chess.pgn
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

def ip_input(screen: pygame.Surface):
    font_title       = pygame.font.Font(None, 64)
    font_option      = pygame.font.Font(None, 50)
    font_help        = pygame.font.Font(None, 30)
    shadow_color     = (128, 119, 97)
    highlight_color  = (187, 250, 245)
    font_color       = (130, 179, 175)
    background_color = (222, 210, 177)
    textinput = pygame_textinput.TextInputVisualizer(font_object=font_option)
    clock = pygame.time.Clock()
    run = True
    while run:
        screen.fill(background_color)
        title_surface = font_title.render("Waiting for IP", True, font_color)
        title_shadow = font_title.render("Waiting for IP", True, shadow_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_shadow, title_rect.move(3, 3))
        screen.blit(title_surface, title_rect)
        title_surface = font_option.render(f"IP: ", True, font_color)
        title_shadow = font_option.render("IP: ", True, shadow_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2-150, HEIGHT // 2))
        screen.blit(title_shadow, title_rect.move(3, 3))
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
            pygame.draw.rect(screen, highlight_color, [WIDTH/2 + 140, HEIGHT/2-18, 160, 50]) 
            
        else: 
            pygame.draw.rect(screen, shadow_color, [WIDTH/2 + 140, HEIGHT/2-18, 160, 50])

        title_surface = font_option.render("Connect", True, font_color)
        title_shadow = font_option.render("Connect", True, shadow_color)
        title_rect = title_surface.get_rect(center=(WIDTH // 2 + 80 + 140, HEIGHT // 2+2.5))
        screen.blit(title_shadow, title_rect.move(3, 3))
        screen.blit(title_surface, title_rect)

        pygame.display.update()
        clock.tick(30)
    return SERVER_IP


def main(debug=False):
    global logger
    screen, board, logger, clock, images = init_game(debug, __name__)

    pygame.display.set_caption("Czess - LAN multiplayer - client")

    game = Game(screen, board, images)

    SERVER_IP = ip_input(screen)

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

        game.loop(events, multiplayer="client")

        if not game.game_end:
            if game.board.turn == chess.BLACK:
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
    except KeyboardInterrupt:
        logger.info("User Exited")
    except Exception as e:
        logger.error(e)
        raise e
