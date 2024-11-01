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
'white_king': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAQhJREFUWIXdl70NwjAQhV8QA1HANAg2QFSZggqxASjTJAUbmYLYcSKH3LuzsODr7ETnp/           u1AQ6XWKf2xKyYw7u2iQ91XdvgfKxHe9FaxJoQAADoRQQOpw2AmjUTqIh/KddKbTMCgCEMgcftOVpf7xfKLpMDSd4h0GMWYBWRRYAFVkC13e1nP7Lx1whIMk3ErwqwHA7wZeiZ6wm0PY0ABwwd0Xugjz9ts7gH6Fng+eABiv/   ohBZUSRgPpLgMNY1IXQW5bJrHMWDzws95IIiYKUPaXvEqKC7AXIaALQxZqsAiQhqC8BBZYvJQWUSiVHQwoLuiF09C9TiOsVzLTAKs90FAnq3su1Bs/wVrCW/YHDwYhQAAAABJRU5ErkJggg==',
	
'black_king': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAQxJREFUWIXdlzsOwjAQRCeIijZNzoA4QqRIKTg0BRISR0CcgYY2bSiIHSeyyc5uhAWvcz67o/3ZBjj6yDr2TMyGcd42dei0b5sa+8Nx8ixYi9gSAgAAgwhPVXbA26mKgviWCq3UNiMAGNPgeTx3k/X9dqLsMjUQpSo70/9mAVYRqwiwwAoozpdr8iWbf42AKPNC/KoAi3OAb0NHaibQ9jQCemCciC4CQ/5pm9kjQO8Fjg8RoPiPSWhBVYThhhS2oWYQqbtgLZvm7RiwReHnIuBFJNqQtpe9C7ILMLchYEvDKl1gESFNgb+ILDG7qCwiUSpyDOiO6NmLUL0dh1iOZSYB1vMgIK9W9l4otv8ChF5hDEafNAYAAAAASUVORK5CYII=',

'white_queen': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAATBJREFUWIXFVskNg0AMHKIUxAOqQdAB4kUVeUV0EEQ18KCjzQevloTDxyJG4oFAnll7bC9gg1seNR4W8mkc0FQtCblcQEjipnHwLxsi2IK4AojQAXALIQCgrNNfEU6SlUQioO/mFWkI+kZ4f16s+NwMJFleoKxTT57lhSelb1Jy9k8BfFqbql2RZnmhiisWEJovBGVDcnrA1oZ/5BqYBVjIAXkJgPP2EsWM4oEwC1IP3J4BC9w0Dq6pWtNC0prwbBdcLsBjayxLoK3X3mnF8Z5KAQhL0HczuV+M2zOgasPfWaDdA0CkXWAxonodx4orNiFzHbNxewaimBBYteKlJty9EQG6kcy+FQP79Sds+OA0PkfA4an3RARCDjmizIEtci6iCdDeDdXLyEpMEJnwivhfQ0iOok/rRwsAAAAASUVORK5CYII=',

'black_queen': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAThJREFUWIXFlj0KhDAQhZ/LVrY2ewbxCIJg4aG3EASPsOwZbGxts40Jo+vP/ER8IGgz78vkJSNgk5sftR4W87oqkReNB7kcgJq4uirDxwYEG4gL4A0dADcbAgBe2bSGcJKuPLmkxCSYUohhTEHBuOJ2IGm7Hq9sCuZt12MY0/BOob6fNwAkrMISWpC25kWzMG27XlVXDEDDR+W7IVk9YDuGf+YamQEs5oB8C4Dz4yWqGSUDtAvSDNzeAYtcXZUuLxrTQNKG8GwWXA4QtL6WpdLu195qxfVEw4iKbsEwpj79Yt3eAdUxXN8F2jkARJoFliCqx3GsuuIQMscxW7d3IEoIgcVRvDSEu39EgO5K5tI6YH//vTZycFqfA3C46j0IAnLoEeUe2DLnKhqA9t9QPYysxl6iEF5R/wcwAnn3Ss6U4wAAAABJRU5ErkJggg==',

'white_rook': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAR5JREFUWIXtVkEOgjAQHNSL7/ABctDExKcY+AHhxF3Pnow/0PAVEwMHfI6nepCSSijtbks4yCQkTbrsTtvZaYF/R0CIFco/QhMTtOL8EiiLHJvtAWmcAQCiJPwJkHOX29k695xSHACW71VncXVut97j+XocAZxMiWeWBBpESdhZXEfKOwHfGJ0AWYQ63K9VM6aI0MsOqMWpoOwAoPS/3A1ZvF41Ny+NRFnkoibTfGmcyTEJCy4LVQ8uRzB6F4xOgC1CX3nJGujzAuB7IVEwHQHHMERZ5J2tR7FgCbYPqFfv5AMuIItQ14atS2kQEfa+B7gkbIIEYDYgDQljDRMB46r7SChEtHW8i5Dakl4JcPyAbUSuhSWsReiAQd+HzvgAMZhsdiPLDYUAAAAASUVORK5CYII=',

'black_rook': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAQpJREFUWIXtlrEKgzAQhn9Lp64ufQbxEQKBDD50h0Khj1D6DF26uqZDjVzFmNzlxKH+IAg5vS/J3Z8A/66KEevJNz4SU03idAGcNbje7mjaDgBwrvufgDD2fFzUAbyzBgDwep9mk9MxANkQh0yAUee6n00eg1IH0NbmAOwijEmy/4DSCtDkXHFWACD9P+2KYdbS//IgnDV+gBmfpu3CO0tHKQWth5It2LwLNgcQF6HWf9k1sOQFwPdA4mjfAolheGfNbOtxLDhI7AP06N19oETsIoy14eRQWqUIF+8DUoicIA+kDSgCkcyRAkjOegmCgETzqBchtyVVASR+IDai0sRB2UVYoFXvh8X6AFolYQBvTSZ4AAAAAElFTkSuQmCC',

'white_bishop': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAPFJREFUWIXdlcENgkAQRR/GgjxoNUY6MJyowpOxAw3VwMGO1gviokJ2/6zZ4E84kJiZx/jnDyxcrn9krRKBZAFwXdtQlTUYpqACuK5thhcLRGFtDrDd7anKmvP1FF1zLQCMGsMwAUkmAEvjp0xbcDhuzACKB2DacNH1kpjwdrkDSCbMPgHVAwWAF0RScwtAsiAy3wLrJiz6GAGvDVAlrWHKmlIU+wb0J9DnQJSyT0AOovcpKCkI/7AFOQA+jhHoaRj7n31tDvpFDP2hg/H6BUAE1Q8BmPzqOQgPZLZHUhMqsZwMQL0JSQAsBynKhD+sn08PK9Zd+HGnVCYAAAAASUVORK5CYII=',

'black_bishop': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAPdJREFUWIXdlTEOgkAQRR/GypbGMxiPQEJC4aEpTEw8AuEMNra0a4MIKmT3z5oN/oSCBGbezs78gZXL9Y+sTSSQJACuKgsOxxMYqqACuKoshhcLhAIwSb7PO9qmliG2AsCg8+UKDBWQZAKwJH7KNAX7vDMDZOJ/c3cdHE8BmDQhwO2+A6Bt6uCYySug9kAGMDIiKbkFIKkRTWSdhFUvI+A1AaqkMYwZU7LicQOOK9D7QJCSV0A2ovcqKC4I/zAFKQA+lhHobhh6Z1+Tg74RfT90MB0/Dwiv+D4As6deghiBLOaI2oSKLUcDUHdCFADLQgpqwh/GT6cHfvlNAetL/IIAAAAASUVORK5CYII=',

'white_knight': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAQBJREFUWIXtV0EKwjAQ3IgP8qCvEfsD6amv6Kn4g4qv0YM/0ktTQtokM8lGEB0ItJRmJrPTbCryhx5e06Cw0SJ+3G9ZL28LiSWX2MLkkoeI94cjNW+OgKTdjAg2A1Ct26YTAQPJOLAgv16e8/XpvFs8G8Y+yVEsYBh7u+JVpESgX0HQ+rbpLMl8zwB1IChgxWq/9lEOJITJ4HmhM96IongntOFjkq8qoFSEigBXBAtEgJl2NgisC2oO5AIVQLlQQwAMZPt1wXZDtLafb8do81ERoDknXYJYTxCplwHo/OeJgOZHBFAnXveQgrjxNRsRBHf1KEr+C4qILagQVpz/h/EG4S5wIzA/JrwAAAAASUVORK5CYII=',

'black_knight': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAQhJREFUWIXtVjEKg0AQnAupbG18g/iEQCCFj7YIBPIE8Q02trZJ48nlxDh7u9okAweCuDPOzt0t8IcdXtMS4WRFfLtekj4+K4mRSuzhUsnXiO+Pp6huioBNuyUipBmgel1WNUAGUuLAgrwfsvm5yMfFu65tNjnUu2AiQT9kHwvgnGB3war1ZVXPIgJSGpptiCIfwzY4AOjaJv5jdQs2gxdZ7aL1FeoM+PBJkm8qQCvCREAoQgpGgJtONgpSF8wcSAUrQOTCHgJoMMdvCOltyPb2+OuYvXxMBFjWFLdg7Vj2d8JeGaDmv0gEVZ8RIJp4wyHlkIFEC1MB4d+zUA0kGmIPUQh3rP/DeANJk2NzT0gk7wAAAABJRU5ErkJggg==',

'white_pawn': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAALhJREFUWIXtlsENwjAQBCcUSgu8qIIXSgdEqSZ5pCPzQCADinK3vkSgeJ+WvTuyz2fD3tWI61KUnwKQxqF/G+jaCYDr7eL29AJ8hZdCeABmw0sgDg6AVVQBKsBfXcNZiC0b0Qsiyk+tgQZgHHpOx7McXgIQJvkI8jro2kk6f/iBHagAFSCkE4J+E8LeAhXCOjHBo/MtKYMw+VsAFv+CnwBPWXYjtAjzcKvCAJTwMAA1HJxFuKL/jnUHJPJSvobi5vYAAAAASUVORK5CYII=',

'black_pawn': 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAALlJREFUWIXtlkEKwjAQRV9d9ijiEQqFLjy05xDP0E3PEBeiRKV05mdalOYvQ/L/I5lMAntXI65LUX4KQBr67m1gnFoAbteL29ML8BVeCuEBmA0vgTg4AFZRBagAf3UNZyG2bEQviCg/tQYagKHvOJ7OcngJQJjkI8jrYJxa6fzhB3agAlSAkE4I+k0IewtUCOvEBI/Ot6QMwuRvAVj8C34CPGXZjdAizMOtCgNQwsMA1HBwFuGK/jvWHVZ4RiRonDhJAAAAAElFTkSuQmCC',

'white_square': 'iVBORw0KGgoAAAANSUhEUgAAAEsAAABLCAYAAAA4TnrqAAAAAXNSR0IArs4c6QAAAaJJREFUeJzt3EFygkAUANGBSm4Qz5L77+JZcoO4IAtrrAH+gI1IifTbmVjqdH2QhUzz9/PVpQ19fv+u9lqX82m117rHxzNedM0gS9/nGSFHsfIHyG8WPb6cT5sFWWouZF5H+dza46yJDsPoya8e5xHROqPJvMUqS5feOdJQbf357+3wH1OP393c+m+xtv5m2Yuyy+Q568ii4blNVg5kqKuoR1t7ssZ6h6FTNVYejk4WMDpnqS88Z3npEAsPQycr5rfhQsYCjAUYCzAWYCygTcnLhjm5j5MFGAswFmAswFiAsYCm67pNf+uwZ04WYCzAWICxAGMBxgKMBRgLMBZgLMBYgLEAYwHGAowFGAswFmAsoPUXf/e5nE9OFmEswFiAsQBjAcYC2pS8YWBOeCerphkLMBZgLMBYgLEA7zec4f2GgHeyAt5QvlDvMHS6+oZbXzlZgHvRVEzuRZNSf6Otox6S5dqrW0I5TbHqOWs4TUebrrn1u+dfun/Pv9G3YbSzYr6syH/b+8SV68iXB7UdJUvhZD3qFaZwk31K1zD1Qfe8A+4/FA68EXoO0LUAAAAASUVORK5CYII=',

'black_square': 'iVBORw0KGgoAAAANSUhEUgAAAEsAAABLCAYAAAA4TnrqAAAAAXNSR0IArs4c6QAAAYBJREFUeJzt3EGSgjAUANFAeQIOyOE4A/ebWeFg+BBbwFHSb6elU/O7EmShacZx/Elv1vf97r8xDMMB/wnTnBHriBh7nRETxfqECEcjUdvoyTxK3/eXDJVSPNvarItYV41CRR3a6AXzpVlLvPmc0/z57Lf5g//4hPlUUYvwmlV60xU9M+fqBb6W7Zfbmv3h1qHWQFvmK664DfXnHstVFZt3cWUBxgKMBRgLMBZgLMBYgLGANiVvSEumPq4swFiAsQBjAcYCjAUYCzAW0HRd9/YvhnwrVxZgLMBYgLEAYwHGAowFGAswFmAswFiAsQBjAcYCjAUYC2hr+er2XsMwuLIIYwHGAowFGAswFmAswFhAm1I9vyl81dTHlQUYCzAWYCzAWICxAGMBxgLusbwxjXlUwYvC87PyA3xq+NVYPmu0026LZ1ZeWIut2YvbsIZVldJzcy7Oz6olTknU4iFWdI2qZUtGB6zlsy+2YS1xSqIOniYJFofnlAKnxCr51hNwfwEpF31vfEugTAAAAABJRU5ErkJggg==',

'chess_board': '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',

}