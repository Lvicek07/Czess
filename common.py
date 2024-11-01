import chess
import pygame
from typing import Dict
import random
import logging as log
import chess.pgn
import base64
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
                #print("Game ended: ", self.board.outcome())
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
                                self.selected_piece = None
                                self.selected_square = None
                    elif piece:
                        if piece.color == self.color:
                            self.selected_piece = piece
                            self.selected_square = square


class AI:
    def __init__(self, color: bool, difficulty: str) -> None:
        logger.debug("Initializing AI")
        self.difficulty     = difficulty
        self.color          = color
        self.selected_piece = None  # Přidání atributu selected_piece

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
            board.push(move)
            self.selected_piece = None  # Reset selected_piece po tahu
            logger.debug("AI moved piece")
        return move

    def easy_move(self, board: chess.Board) -> chess.Move:
        """AI s náhodnými tahy."""
        return random.choice(list(board.legal_moves))

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
    images = {}
    pieces = ["king", "queen", "rook", "bishop", "knight", "pawn", "square"]
    colors = ["white", "black"]

    if debug:
        for piece in pieces:
            for color in colors:
                img = pygame.image.load(f"assets/{piece}/{color}.png")
                if piece == "square":
                    img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
                else:
                    img = pygame.transform.scale(img, (SQUARE_SIZE-(IMAGE_OFFSET*2), SQUARE_SIZE-(IMAGE_OFFSET*2)))
                images[f"{color}_{piece}"] = img
                logger.debug(f"Succesfully loaded {color}_{piece}")

        img = pygame.image.load(f"assets/ChessBoard.png")
        #img = pygame.transform.scale(img, (600, 600))
        images["chess_board"] = img
        logger.debug("Succesfully loaded chess_board")
                    
        return images
    else:    
        for piece in pieces:
            for color in colors:
                try:
                    img_b64 = IMAGES[f"{color}_{piece}"]
                except:
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
        try:
            img_b64 = IMAGES[f"chess_board"]
        except:
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