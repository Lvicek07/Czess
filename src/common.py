import chess
import pygame
from typing import Dict
import random
import logging as log
import chess.pgn
import base64
import time
import io
import os

class Game:
    def __init__(self, screen: pygame.Surface, board: chess.Board, images: dict[str, str]) -> None:
        logger.debug("Initializing Game logic")
        self.board     = board
        self.players   = {"white": Player(chess.WHITE), "black": Player(chess.BLACK)}
        self.moves     = dict()
        self.last_move = None
        self.game_end  = False
        self.move_num  = 1
        self.images    = images
        self.screen    = screen

        # Předání zvukového souboru hráčům při jejich inicializaci
        sound_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds', 'move-sound.mp3')
        self.move_sound = pygame.mixer.Sound(sound_path)
        
        # Předání zvuku hráčům
        self.players["white"].set_move_sound(self.move_sound)
        self.players["black"].set_move_sound(self.move_sound)

    def loop(self, events: tuple[pygame.event.Event, ...], multiplayer=None) -> None:
        if not self.game_end:
            if multiplayer == "client":
                if self.board.turn == chess.BLACK:
                    self.players["black"].on_move(self.board, events)
                    self.game_state = "On turn: Black"
            elif multiplayer == "server":
                if self.board.turn == chess.WHITE:
                    self.players["white"].on_move(self.board, events)
                    self.game_state = "On turn: White"
            else:
                if self.board.turn == chess.WHITE:
                    self.players["white"].on_move(self.board, events)
                    self.game_state = "On turn: White"
                else:
                    self.players["black"].on_move(self.board, events)
                    self.game_state = "On turn: Black"
            
            draw_board(self.board, self.screen, (self.players["white"], self.players["black"]), self.images)

            if self.board.outcome() != None:
                self.game_state = f"Game ended: {self.board.outcome().result}"
                self.game_end_menu.state = self.game_state
                self.game_end = True

            self.screen.blit(FONT.render(self.game_state, True, FONT_COLOR), (710,0))
            try:
                if self.board.peek() != self.last_move:
                    self.last_move = self.board.peek()
                    self.moves[self.move_num] = self.last_move
                    self.move_num += 1
            except IndexError:
                pass
            print_game_log(self.screen, self.moves)


class Player:
    def __init__(self, color: bool) -> None:
        logger.debug("Initializing Player")
        self.is_playing      = False
        self.color           = color
        self.selected_piece  = None
        self.selected_square = None
        self.move_sound      = None  # Inicializace move_sound jako None
        
    def set_move_sound(self, move_sound: pygame.mixer.Sound) -> None:
        """Přiřadí zvukový efekt pro pohyb do hráče."""
        self.move_sound = move_sound

    def on_move(self, board: chess.Board, events: tuple[pygame.event.Event, ...]) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] >= 50 and mouse_pos[1] >= 50:
                    x = int((mouse_pos[0]-50) // SQUARE_SIZE)
                    y = 7 - int((mouse_pos[1]-50) // SQUARE_SIZE)
                    square = chess.square(x, y)
                    piece = board.piece_at(square)

                    if self.selected_piece:
                        if square == self.selected_square:
                            self.selected_piece = None
                            self.selected_square = None
                            logger.debug(f"Player {get_color(self.color)} cancelled move")
                        elif board.color_at(square) == self.color:
                            self.selected_piece = piece
                            self.selected_square = square
                            logger.debug(f"Player {get_color(self.color)} reselected piece {chess.piece_name(self.selected_piece.piece_type)}")
                        else:
                            move = chess.Move(self.selected_square, square)
                            if move in board.legal_moves:
                                board.push(move)
                                logger.debug(f"Player {get_color(self.color)} moved piece {chess.piece_name(self.selected_piece.piece_type)} from {chess.square_name(self.selected_square)} to {chess.square_name(square)}")
                                
                                # Přehrát zvuk po provedení tahu
                                self.play_move_sound()
                                self.selected_piece = None
                                self.selected_square = None
                    elif piece:
                        if piece.color == self.color:
                            self.selected_piece = piece
                            self.selected_square = square

    def play_move_sound(self):
        """Přehrát zvuk pohybu figurky."""
        if self.move_sound:  # Ověření, zda je zvuková soubor přiřazen
            self.move_sound.play()



class AI:
    def __init__(self, color: bool, difficulty: str) -> None:
        logger.debug("Initializing AI")
        self.difficulty     = difficulty
        self.color          = color
        self.selected_piece = None  # Přidání atributu selected_piece
        self.capture_sound = pygame.mixer.Sound("../assets/sounds/capture.mp3")  # Zvuk pro zachycení

    def on_move(self, board: chess.Board, events: tuple[pygame.event.Event, ...]) -> chess.Move:
        "DO NOT REMOVE EVENTS, Game class will parse events"
        if self.difficulty == "easy":
            move = self.easy_move(board)
        elif self.difficulty == "medium":
            move = self.medium_move(board)
        elif self.difficulty == "hard":
            move = self.hard_move(board)
        elif self.difficulty == "Fales":
            move = self.fales_move(board)
        else:
            raise ValueError("Difficulty not selected")

        if move:
            if board.is_capture(move):  # Kontrola, zda tah vede k zachycení figury
                self.capture_sound.play()  # Přehrání zvuku pro zachycení
            board.push(move)
            self.selected_piece = None  # Reset selected_piece po tahu
            logger.debug("AI moved piece")
        return move

    def easy_move(self, board: chess.Board) -> chess.Move:
        """AI s náhodnými tahy, počká 1 vteřinu před výběrem."""
        time.sleep(1)  # Počkejte 1 sekundu
        return random.choice(list(board.legal_moves))  # Vybírá náhodný legální tah

    def medium_move(self, board: chess.Board) -> chess.Move:
        """AI prioritizující zachycení a kontrolu centrálních polí."""
        legal_moves = list(board.legal_moves)
        capture_moves = [move for move in legal_moves if board.is_capture(move)]
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]

        # Prioritizace zachycení figury
        if capture_moves:
            return random.choice(capture_moves)

        # Prioritizace kontroly centrálních polí
        central_moves = [move for move in legal_moves if move.to_square in center_squares]
        if central_moves:
            return random.choice(central_moves)

        # Pokud není zachycení ani kontrola centra, zvolí náhodný tah
        return random.choice(legal_moves)

    def hard_move(self, board: chess.Board) -> chess.Move:
        """AI hledá nejlepší tah s důrazem na agresivitu."""
        best_move  = None
        best_value = -9999

        for move in board.legal_moves:
            board.push(move)
            board_value = self.evaluate_board(board)
            board.pop()

            # Zvýšená hodnota pro agresivní tahy (zachycení a kontrola centra)
            if board.is_capture(move):
                board_value += 5
            elif move.to_square in [chess.D4, chess.E4, chess.D5, chess.E5]:
                board_value += 3

            if board_value > best_value:
                best_value = board_value
                best_move = move

        return best_move

    def fales_move(self, board: chess.Board) -> chess.Move:
        """AI s hlubokou analýzou tahů."""
        best_move, _ = self.minimax(board, depth=3, maximizing_player=True)
        return best_move

    def minimax(self, board: chess.Board, depth: int, maximizing_player: bool = True) -> tuple[None, int] | tuple[chess.Move, int]:
        if depth == 0 or board.is_game_over():
            return None, self.evaluate_board(board)

        best_move = None
        if maximizing_player:
            best_value = -9999
            for move in board.legal_moves:
                board.push(move)
                _, value = self.minimax(board, depth - 1, False)
                board.pop()

                if value > best_value:
                    best_value = value
                    best_move = move
        else:
            best_value = 9999
            for move in board.legal_moves:
                board.push(move)
                _, value = self.minimax(board, depth - 1, True)
                board.pop()

                if value < best_value:
                    best_value = value
                    best_move = move
        return best_move, best_value
        
    def evaluate_board(self, board: chess.Board) -> int:
        """Hodnotí pozici na šachovnici."""
        if board.is_checkmate():
            return 10000 if board.turn == chess.BLACK else -10000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

        value = 0
        for piece in board.piece_map().values():
            piece_value = piece_values[piece.piece_type]
            value += piece_value if piece.color == self.color else -piece_value

        # Přidání strategického hodnocení
        value += self.position_score(board)

        return value


    def position_score(self, board: chess.Board) -> int:
        """Vyhodnocení pozice na základě umístění figur."""
        score = 0
        piece_square_values = {
            chess.PAWN: [0, 0, 0, 0, 0, 0, 0, 0],
            chess.KNIGHT: [-5, -4, -3, -3, -3, -3, -4, -5],
            chess.BISHOP: [-4, -2, -1, -1, -1, -1, -2, -4],
            chess.ROOK: [-2, -1, 0, 0, 0, 0, -1, -2],
            chess.QUEEN: [-1, 0, 0, 0, 0, 0, 0, -1],
            chess.KING: [0, 1, 1, 3, 3, 1, 1, 0],
        }

        for square, piece in board.piece_map().items():
            piece_value = piece_square_values[piece.piece_type]
            if piece.color == self.color:
                score += piece_value[square // 8]
            else:
                score -= piece_value[square // 8]

        return score

def get_color(color: bool) -> str:
    return "white" if color==True else "black"
    
def init_game(debug=False, name=__name__) -> tuple[pygame.Surface, chess.Board, log.Logger, pygame.time.Clock, Dict[str, pygame.Surface], pygame.font.Font]:
    global logger
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    logger = log.getLogger(name)
    if debug:
        log.basicConfig(level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
    else:
        log.basicConfig(level=log.WARNING,  format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
    logger.debug("Initializing app")

    logger.debug("Initializing pygame")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    logger.debug("Initializing chess board logic")
    board = chess.Board()
    logger.debug("Initializing frame limiter")
    clock = pygame.time.Clock()

    logger.debug("Loading images")
    images = load_images(debug)
    return screen, board, logger, clock, images

def load_images(debug=False) -> Dict[str, pygame.Surface]:
    # Určte cestu k kořenovému adresáři projektu (Czess)
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # Dva kroky zpět k Czess
    assets_dir = os.path.join(project_dir, "assets")  # Cesta k assets složce

    images = {}
    pieces = ["king", "queen", "rook", "bishop", "knight", "pawn", "square"]
    colors = ["white", "black"]

    if debug:
        for piece in pieces:
            for color in colors:
                img_path = os.path.join(assets_dir, piece, f"{color}.png")
                try:
                    img = pygame.image.load(img_path)
                except FileNotFoundError:
                    logger.error(f"Image not found: {img_path}")
                    continue
                
                if piece == "square":
                    img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
                else:
                    img = pygame.transform.scale(img, (SQUARE_SIZE-(IMAGE_OFFSET*2), SQUARE_SIZE-(IMAGE_OFFSET*2)))
                
                images[f"{color}_{piece}"] = img
                logger.debug(f"Succesfully loaded {color}_{piece} from {img_path}")

        img_path = os.path.join(assets_dir, "ChessBoard.png")
        try:
            img = pygame.image.load(img_path)
            images["chess_board"] = img
            logger.debug(f"Succesfully loaded chess_board from {img_path}")
        except FileNotFoundError:
            logger.error(f"Image not found: {img_path}")
                    
        return images
    else:
        for piece in pieces:
            for color in colors:
                try:
                    img_b64 = IMAGES[f"{color}_{piece}"]
                except KeyError:
                    img_b64 = ERROR_IMAGE
                    logger.error(f"! Could not load image of {color} {piece}, using error image")
                
                img_data = base64.b64decode(img_b64)
                img_bytes = io.BytesIO(img_data)
                img = pygame.image.load(img_bytes)
                
                if piece == "square":
                    img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
                else:
                    img = pygame.transform.scale(img, (SQUARE_SIZE-(IMAGE_OFFSET*2), SQUARE_SIZE-(IMAGE_OFFSET*2)))
                
                images[f"{color}_{piece}"] = img
                if img_b64 == ERROR_IMAGE:
                    logger.debug("Succesfully loaded error image")
                else:
                    logger.debug(f"Succesfully loaded {color}_{piece}")
        
        # Načítání chess boardu
        try:
            img_b64 = IMAGES[f"chess_board"]
        except KeyError:
            img_b64 = ERROR_IMAGE
            logger.error(f"! Could not load image of chess board, using error image")
        
        img_data = base64.b64decode(img_b64)
        img_bytes = io.BytesIO(img_data)
        img = pygame.image.load(img_bytes)
        images[f"chess_board"] = img
        if img_b64 == ERROR_IMAGE:
            logger.debug("Succesfully loaded error image")
        else:
            logger.debug("Succesfully loaded chess_board")
        
        return images

def draw_piece(piece: chess.Piece, screen: pygame.Surface, pos: tuple[int, int], piece_images: Dict[str, pygame.Surface]) -> None:
    color = get_color(piece.color)
    type  = chess.piece_name(piece.piece_type)
    x, y  = pos
    x     = x*SQUARE_SIZE+IMAGE_OFFSET+50
    y     = y*SQUARE_SIZE+IMAGE_OFFSET+50
    img   = piece_images[f"{color}_{type}"]

    screen.blit(img, (x, y))

def draw_square_overlay(screen: pygame.Surface, row: int, col: int) -> None:
    pygame.draw.rect(screen, (128, 255, 128), (col * SQUARE_SIZE+50, row * SQUARE_SIZE+50, SQUARE_SIZE, SQUARE_SIZE), width=15)

def draw_board(board: chess.Board, screen: pygame.Surface, players: tuple[Player, Player], images: Dict[str, pygame.Surface]) -> None:
    legal_moves = None
    screen.fill(EGGSHELL)
    screen.blit(images["chess_board"], (0, 0))

    if board.turn == chess.WHITE:
        if players[0].selected_piece:
            row = 7 - chess.square_rank(players[0].selected_square)
            col = chess.square_file(players[0].selected_square)
            pygame.draw.rect(screen, (0, 255, 0), (col * SQUARE_SIZE+50, row * SQUARE_SIZE+50, SQUARE_SIZE, SQUARE_SIZE))
            legal_moves = [move for move in board.legal_moves if move.from_square == players[0].selected_square]
    else:
        if players[1].selected_piece:
            row = 7 - chess.square_rank(players[1].selected_square)
            col = chess.square_file(players[1].selected_square)
            pygame.draw.rect(screen, (0, 255, 0), (col * SQUARE_SIZE+50, row * SQUARE_SIZE+50, SQUARE_SIZE, SQUARE_SIZE))
            legal_moves = [move for move in board.legal_moves if move.from_square == players[1].selected_square]

    if legal_moves:    
        for move in legal_moves:
            row = 7 - chess.square_rank(move.to_square)
            col = chess.square_file(move.to_square)
            draw_square_overlay(screen, row, col)

    x = 0
    y = 0
    for char in list(board.board_fen()):
        if char == "/":
            x = 0
            y += 1
        elif char.isnumeric():
            x += int(char)
        else:
            piece = chess.Piece.from_symbol(char)
            draw_piece(piece, screen, (x, y), images)
            x += 1

def print_game_log(screen: pygame.Surface, moves: Dict[int, chess.Move]) -> None:
    if moves:
        if len(moves) > 15:
            moves = dict(list(moves.items())[-15:])
        x = FONT_SIZE + 5
        n = 1
        for index, move in moves.items():
            text = f"{index}. {move.uci()}"
            screen.blit(FONT.render(text, True, FONT_COLOR), (710,x))
            x += FONT_SIZE + 5
            n += 1
    else:
        screen.blit(FONT.render("No moves", True, FONT_COLOR), (710,FONT_SIZE+5))

pygame.font.init()
WIDTH, HEIGHT   = 1200, 700 # 600 x 600 herní pole
MENU_WIDTH, MENU_HEIGHT = 800, 600
SQUARE_SIZE     = 600 // 8  # 75
IMAGE_OFFSET    = 2         # Image size = 71x71
ROWS, COLS      = 8, 8
WHITE           = (255, 255, 255)
FONT_TITLE      = pygame.font.Font(None, 64)
FONT_OPTION     = pygame.font.Font(None, 50)
FONT_HELP       = pygame.font.Font(None, 30)
SHADOW_COLOR    = (128, 119, 97)
HIGHLIGHT_COLOR = (187, 250, 245)
FONT_COLOR      = (130, 179, 175)
BACKGROUND_COLOR= (222, 210, 177)
EGGSHELL        = (235, 236, 208)
BLACK           = (0, 0, 0)
FONT_COLOR      = BLACK
FONT_SIZE       = 30
FONT            = pygame.font.SysFont('consolas', FONT_SIZE)
ERROR_IMAGE     = "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"

# Base64 representation of used images (file loading not worky in exe version)
# Antoníne, pokud se s tím chceš srát, tu vlož ten text z images_b64.txt
# Bez jakýchkoliv změn, prostě překopíruj ten text to vnitřku závorek
IMAGES = {
	'white_king': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAQhJREFUWIXdl70NwjAQhV8QA1HANAg2QFSZggqxASjTJAUbmYLYcSKH3LuzsODr7ETnp/u1AQ6XWKf2xKyYw7u2iQ91XdvgfKxHe9FaxJoQAADoRQQOpw2AmjUTqIh/KddKbTMCgCEMgcftOVpf7xfKLpMDSd4h0GMWYBWRRYAFVkC13e1nP7Lx1whIMk3ErwqwHA7wZeiZ6wm0PY0ABwwd0Xugjz9ts7gH6Fng+eABiv/ohBZUSRgPpLgMNY1IXQW5bJrHMWDzws95IIiYKUPaXvEqKC7AXIaALQxZqsAiQhqC8BBZYvJQWUSiVHQwoLuiF09C9TiOsVzLTAKs90FAnq3su1Bs/wVrCW/YHDwYhQAAAABJRU5ErkJggg==',
	'black_king': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAQxJREFUWIXdlzsOwjAQRCeIijZNzoA4QqRIKTg0BRISR0CcgYY2bSiIHSeyyc5uhAWvcz67o/3ZBjj6yDr2TMyGcd42dei0b5sa+8Nx8ixYi9gSAgAAgwhPVXbA26mKgviWCq3UNiMAGNPgeTx3k/X9dqLsMjUQpSo70/9mAVYRqwiwwAoozpdr8iWbf42AKPNC/KoAi3OAb0NHaibQ9jQCemCciC4CQ/5pm9kjQO8Fjg8RoPiPSWhBVYThhhS2oWYQqbtgLZvm7RiwReHnIuBFJNqQtpe9C7ILMLchYEvDKl1gESFNgb+ILDG7qCwiUSpyDOiO6NmLUL0dh1iOZSYB1vMgIK9W9l4otv8ChF5hDEafNAYAAAAASUVORK5CYII=',
	'white_queen': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAATBJREFUWIXFVskNg0AMHKIUxAOqQdAB4kUVeUV0EEQ18KCjzQevloTDxyJG4oFAnll7bC9gg1seNR4W8mkc0FQtCblcQEjipnHwLxsi2IK4AojQAXALIQCgrNNfEU6SlUQioO/mFWkI+kZ4f16s+NwMJFleoKxTT57lhSelb1Jy9k8BfFqbql2RZnmhiisWEJovBGVDcnrA1oZ/5BqYBVjIAXkJgPP2EsWM4oEwC1IP3J4BC9w0Dq6pWtNC0prwbBdcLsBjayxLoK3X3mnF8Z5KAQhL0HczuV+M2zOgasPfWaDdA0CkXWAxonodx4orNiFzHbNxewaimBBYteKlJty9EQG6kcy+FQP79Sds+OA0PkfA4an3RARCDjmizIEtci6iCdDeDdXLyEpMEJnwivhfQ0iOok/rRwsAAAAASUVORK5CYII=',
	'black_queen': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAThJREFUWIXFlj0KhDAQhZ/LVrY2ewbxCIJg4aG3EASPsOwZbGxts40Jo+vP/ER8IGgz78vkJSNgk5sftR4W87oqkReNB7kcgJq4uirDxwYEG4gL4A0dADcbAgBe2bSGcJKuPLmkxCSYUohhTEHBuOJ2IGm7Hq9sCuZt12MY0/BOob6fNwAkrMISWpC25kWzMG27XlVXDEDDR+W7IVk9YDuGf+YamQEs5oB8C4Dz4yWqGSUDtAvSDNzeAYtcXZUuLxrTQNKG8GwWXA4QtL6WpdLu195qxfVEw4iKbsEwpj79Yt3eAdUxXN8F2jkARJoFliCqx3GsuuIQMscxW7d3IEoIgcVRvDSEu39EgO5K5tI6YH//vTZycFqfA3C46j0IAnLoEeUe2DLnKhqA9t9QPYysxl6iEF5R/wcwAnn3Ss6U4wAAAABJRU5ErkJggg==',
	'white_rook': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAR5JREFUWIXtVkEOgjAQHNSL7/ABctDExKcY+AHhxF3Pnow/0PAVEwMHfI6nepCSSijtbks4yCQkTbrsTtvZaYF/R0CIFco/QhMTtOL8EiiLHJvtAWmcAQCiJPwJkHOX29k695xSHACW71VncXVut97j+XocAZxMiWeWBBpESdhZXEfKOwHfGJ0AWYQ63K9VM6aI0MsOqMWpoOwAoPS/3A1ZvF41Ny+NRFnkoibTfGmcyTEJCy4LVQ8uRzB6F4xOgC1CX3nJGujzAuB7IVEwHQHHMERZ5J2tR7FgCbYPqFfv5AMuIItQ14atS2kQEfa+B7gkbIIEYDYgDQljDRMB46r7SChEtHW8i5Dakl4JcPyAbUSuhSWsReiAQd+HzvgAMZhsdiPLDYUAAAAASUVORK5CYII=',
	'black_rook': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAQpJREFUWIXtlrEKgzAQhn9Lp64ufQbxEQKBDD50h0Khj1D6DF26uqZDjVzFmNzlxKH+IAg5vS/J3Z8A/66KEevJNz4SU03idAGcNbje7mjaDgBwrvufgDD2fFzUAbyzBgDwep9mk9MxANkQh0yAUee6n00eg1IH0NbmAOwijEmy/4DSCtDkXHFWACD9P+2KYdbS//IgnDV+gBmfpu3CO0tHKQWth5It2LwLNgcQF6HWf9k1sOQFwPdA4mjfAolheGfNbOtxLDhI7AP06N19oETsIoy14eRQWqUIF+8DUoicIA+kDSgCkcyRAkjOegmCgETzqBchtyVVASR+IDai0sRB2UVYoFXvh8X6AFolYQBvTSZ4AAAAAElFTkSuQmCC',
	'white_bishop': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAPFJREFUWIXdlcENgkAQRR/GgjxoNUY6MJyowpOxAw3VwMGO1gviokJ2/6zZ4E84kJiZx/jnDyxcrn9krRKBZAFwXdtQlTUYpqACuK5thhcLRGFtDrDd7anKmvP1FF1zLQCMGsMwAUkmAEvjp0xbcDhuzACKB2DacNH1kpjwdrkDSCbMPgHVAwWAF0RScwtAsiAy3wLrJiz6GAGvDVAlrWHKmlIU+wb0J9DnQJSyT0AOovcpKCkI/7AFOQA+jhHoaRj7n31tDvpFDP2hg/H6BUAE1Q8BmPzqOQgPZLZHUhMqsZwMQL0JSQAsBynKhD+sn08PK9Zd+HGnVCYAAAAASUVORK5CYII=',
	'black_bishop': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAPdJREFUWIXdlTEOgkAQRR/GypbGMxiPQEJC4aEpTEw8AuEMNra0a4MIKmT3z5oN/oSCBGbezs78gZXL9Y+sTSSQJACuKgsOxxMYqqACuKoshhcLhAIwSb7PO9qmliG2AsCg8+UKDBWQZAKwJH7KNAX7vDMDZOJ/c3cdHE8BmDQhwO2+A6Bt6uCYySug9kAGMDIiKbkFIKkRTWSdhFUvI+A1AaqkMYwZU7LicQOOK9D7QJCSV0A2ovcqKC4I/zAFKQA+lhHobhh6Z1+Tg74RfT90MB0/Dwiv+D4As6deghiBLOaI2oSKLUcDUHdCFADLQgpqwh/GT6cHfvlNAetL/IIAAAAASUVORK5CYII=',
	'white_knight': 'iVBORw0KGgoAAAANSUhEUgAAAB0AAAAeCAYAAADQBxWhAAAAAXNSR0IArs4c6QAAAPhJREFUSInVlkEOgjAQRafGA7nQ0xi4gWHFKVgRboDhNLrwRrqhpCl05s+0Ev1JEwhhXv70Z1qiP9V7XrAOubDnY1L/eDTCyALzclpgCna+XOF6GqjYShSM7im0d03dEgGhQpyugPfhtTxXt9PqWz92bG0ztB8772xTHFhKb7KtTd36wss7KslpErrRxngvk7W5IInhiYLjopWUeSL5AKGJLQLNAWdBQ7BGHNTNEwaSxm22U4skqMptKSgsafSFQk8ZNJn7HG3IgM+ClqoFt5ebwURl9xS6D0VgsS73UXXTCw92yfVPDgdIoUtElnuvGeYFBekLdffXB0dlcCMeBrm+AAAAAElFTkSuQmCC',
	'black_knight': 'iVBORw0KGgoAAAANSUhEUgAAAB0AAAAeCAYAAADQBxWhAAAAAXNSR0IArs4c6QAAAQFJREFUSInVlsEKgzAMhtOxk1cvPoP4CIPBDj60h8FgjyA+gxevXrdLK12lzZ+0CvuhIBTzkeQ3kehP9bEH1iUX9rjfxC9elTDSwJyMFBiDPV9vOJ4EypYSBaM9hXrXdj0RYCok0x1wXqrtuanX3d00DsnYavfawDQv1c8h4jPm3Bsta9v1G9gDQdJ8MtTUq19iQ0Q0jUOYmaq8rHmCMprgRKXuqTMQ6tgi0BxwFtQHS5SCGjthIEmyzc5UIw4qyrYUFBY3+nyhWwZ15jmrDRnwWdBSseDyxkaim8Elewr9DwVgNm7qUvSn5y/2w5Z4jopA/SwRqZa4FuYEGemAuOfrC1l1Y3OxxFYnAAAAAElFTkSuQmCC',
	'white_pawn': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAALhJREFUWIXtlsENwjAQBCcUSgu8qIIXSgdEqSZ5pCPzQCADinK3vkSgeJ+WvTuyz2fD3tWI61KUnwKQxqF/G+jaCYDr7eL29AJ8hZdCeABmw0sgDg6AVVQBKsBfXcNZiC0b0Qsiyk+tgQZgHHpOx7McXgIQJvkI8jro2kk6f/iBHagAFSCkE4J+E8LeAhXCOjHBo/MtKYMw+VsAFv+CnwBPWXYjtAjzcKvCAJTwMAA1HJxFuKL/jnUHJPJSvobi5vYAAAAASUVORK5CYII=',
	'black_pawn': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAALlJREFUWIXtlkEKwjAQRV9d9ijiEQqFLjy05xDP0E3PEBeiRKV05mdalOYvQ/L/I5lMAntXI65LUX4KQBr67m1gnFoAbteL29ML8BVeCuEBmA0vgTg4AFZRBagAf3UNZyG2bEQviCg/tQYagKHvOJ7OcngJQJjkI8jrYJxa6fzhB3agAlSAkE4I+k0IewtUCOvEBI/Ot6QMwuRvAVj8C34CPGXZjdAizMOtCgNQwsMA1HBwFuGK/jvWHVZ4RiRonDhJAAAAAElFTkSuQmCC',
	'white_square': 'iVBORw0KGgoAAAANSUhEUgAAAEsAAABLCAYAAAA4TnrqAAAAAXNSR0IArs4c6QAAAX5JREFUeJzt3DFuwjAYQGEnB+UKndg6svUWXKmnqHqIdqhSEccOfuAAjt8bI4Twp9+eiIe3w/EnPLj3j8Pd33E6niv8EtawBVYNjHvbArMq1isgxdVEq4L1ikhxNdBuxmoBKNetcAirZaBcBG4s/eAeoUJg6yrC2ivUVOn6iifLrpxZe5+oVGtnWHayeoQKYX3dSaxeoaZy6/fMAokFWmD1vgWnUg5OFkgs0AzLLTgv9nCyQP9YTlW6S5cxfmDLJh+3IUgskFggsUBigcQCiQUSCzR8f30+/I8hreZkgcQCiQUSCyQWSCyQWCCxQGKBxAKJBRILJBZILJBYILFA4zPermqx0/HsZJHEAokFEgskFkgskFggsUBjCM957b+lJp8xfmDzLl3chqAZltM1L/ZwskBigRZYbsW/Ug5OFkgsUBKr962YW392snoFW1t30cU9Pbw1VjIcnlmgIqy9b8nS9RVP1l7ByLq8mQ3knX8gb5MEeU8paBOsa7V6A+4v78h7soH1mawAAAAASUVORK5CYII=',
	'black_square': 'iVBORw0KGgoAAAANSUhEUgAAAEsAAABLCAYAAAA4TnrqAAAAAXNSR0IArs4c6QAAAZtJREFUeJzt3MFtgzAYQOEEdQTa7FD1lCE6fveo1B3SQ+XKgE38CAEM7x0jFfCn3+TS+Pz+8Xk7LdzP99fD12gv1xmehPXyjIvOgfHoPZ6BOSvWEkilhWeZE20WrC0h9ZsTbTLWloFSxc87FQ5h1QaUaypcM+UGe4qsqwhrr1Ch0vUVT5bdeWftfaLiSr41s5N1JKi4sXUnsY4KFcqt33cWSCzQAOvoWzCUcnCyQGKBOlhuwW59DycL9I/lVKWLXZr+BzYs+LgNQWKBxAKJBRILJBZILJBYoPPba7v4P4bUmpMFEgskFkgskFggsUBigcQCiQUSCyQWSCyQWCCxQGKBxAI1a/y6qsbay9XJIokFEgskFkgskFggsUBigZrTaZ2f/ddU8Gn6H1i32MVtCOpgOV3d+h5OFkgs0ADLrfhXysHJAokFSmIdfSvm1p+drKOCja179BCM8IdH+NVYyXD4zgIVYe19S5aur3iy9gpG1oUOG4svXPN7bJGT2XI3rAFu1TP/4rb8rbm50yRDW0Lb/DmloXsPWusJuL/91W1ATzI0vwAAAABJRU5ErkJggg==',
	'chess_board': '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',
}