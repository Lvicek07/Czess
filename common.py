import chess
import pygame
from typing import Dict
import random
import logging as log
import chess.pgn
from os import chdir
from os.path import abspath, dirname

class Player:
    def __init__(self, color: bool) -> None:
        self.is_playing      = False
        self.color           = color
        self.selected_piece  = None
        self.selected_square = None
        self.king            = chess.Piece(chess.KING,   color)
        self.queen           = chess.Piece(chess.QUEEN,  color)
        self.rook_1          = chess.Piece(chess.ROOK,   color)
        self.rook_2          = chess.Piece(chess.ROOK,   color)
        self.knight_1        = chess.Piece(chess.KNIGHT, color)
        self.knight_2        = chess.Piece(chess.KNIGHT, color)
        self.bishop_1        = chess.Piece(chess.BISHOP, color)
        self.bishop_2        = chess.Piece(chess.BISHOP, color)
        self.pawn_1          = chess.Piece(chess.PAWN,   color)
        self.pawn_2          = chess.Piece(chess.PAWN,   color)
        self.pawn_3          = chess.Piece(chess.PAWN,   color)
        self.pawn_4          = chess.Piece(chess.PAWN,   color)
        self.pawn_5          = chess.Piece(chess.PAWN,   color)
        self.pawn_6          = chess.Piece(chess.PAWN,   color)
        self.pawn_7          = chess.Piece(chess.PAWN,   color)
        self.pawn_8          = chess.Piece(chess.PAWN,   color)
        self.pieces          = [self.king, self.queen, self.rook_1, self.rook_2, self.knight_1, self.knight_2, self.bishop_1, self.bishop_2, self.pawn_1, self.pawn_2, self.pawn_3, self.pawn_4, self.pawn_5, self.pawn_6, self.pawn_7, self.pawn_8]

    def on_move(self, board: chess.Board, events: tuple):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x = int(mouse_pos[0] // SQUARE_SIZE)
                y = 7 - int(mouse_pos[1] // SQUARE_SIZE)
                self.square = chess.square(x, y)
                piece = board.piece_at(self.square)

                if self.selected_piece:
                    if self.square == self.selected_square:
                        print("Cancelling move")
                        self.selected_piece = None
                        self.selected_square = None
                    elif board.color_at(self.square) == self.color:
                        print("Cannot place piece on your own pieces")
                    else:
                        move = chess.Move(self.selected_square, self.square)
                        if move in board.legal_moves:
                            board.push(move)
                            self.selected_piece = None
                            self.selected_square = None
                            print("Moved piece")
                        else:
                            print("Invalid move")
                elif piece:
                    if piece.color == self.color:
                        self.selected_piece = piece
                        self.selected_square = self.square
                        print("Piece selected")
                    else:
                        print("Selected enemy piece, cannot move")
                else:
                    print("No piece found")

class AI:
    def __init__(self, color: bool, difficulty: str):
        self.difficulty      = difficulty
        self.is_playing      = False
        self.color           = color
        self.selected_piece  = None
        self.selected_square = None
        self.king            = chess.Piece(chess.KING,   color)
        self.queen           = chess.Piece(chess.QUEEN,  color)
        self.rook_1          = chess.Piece(chess.ROOK,   color)
        self.rook_2          = chess.Piece(chess.ROOK,   color)
        self.knight_1        = chess.Piece(chess.KNIGHT, color)
        self.knight_2        = chess.Piece(chess.KNIGHT, color)
        self.bishop_1        = chess.Piece(chess.BISHOP, color)
        self.bishop_2        = chess.Piece(chess.BISHOP, color)
        self.pawn_1          = chess.Piece(chess.PAWN,   color)
        self.pawn_2          = chess.Piece(chess.PAWN,   color)
        self.pawn_3          = chess.Piece(chess.PAWN,   color)
        self.pawn_4          = chess.Piece(chess.PAWN,   color)
        self.pawn_5          = chess.Piece(chess.PAWN,   color)
        self.pawn_6          = chess.Piece(chess.PAWN,   color)
        self.pawn_7          = chess.Piece(chess.PAWN,   color)
        self.pawn_8          = chess.Piece(chess.PAWN,   color)
        self.pieces          = [self.king, self.queen, self.rook_1, self.rook_2, self.knight_1, self.knight_2, self.bishop_1, self.bishop_2, self.pawn_1, self.pawn_2, self.pawn_3, self.pawn_4, self.pawn_5, self.pawn_6, self.pawn_7, self.pawn_8]

    def on_move(self, board: chess.Board) -> chess.Move:
        if self.difficulty == "easy":
            move = self.easy_move(board)
        elif self.difficulty == "medium":
            move = self.medium_move(board)
        elif self.difficulty == "hard":
            move = self.hard_move(board)
        elif self.difficulty == "Fales":
            move = self.fales_move(board)
        if move:
            board.push(move)

    def easy_move(self, board: chess.Board) -> chess.Move:
        return random.choice(list(board.legal_moves))

    def medium_move(self, board: chess.Board) -> chess.Move:
        return random.choice(list(board.legal_moves))

    def hard_move(self, board: chess.Board) -> chess.Move:
        best_move = None
        best_value = -9999

        for move in board.legal_moves:
            board.push(move)
            board_value = self.evaluate_board(board)
            board.pop()

            if board_value > best_value:
                best_value = board_value
                best_move = move

        return best_move

    def fales_move(self, board: chess.Board) -> chess.Move:
        best_move, _ = self.minimax(board, depth=3)
        return best_move

    def minimax(self, board: chess.Board, depth: int, maximizing_player: bool = True):
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
            return best_move, best_value
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
        if board.is_checkmate():
            return 10000 if board.turn == chess.BLACK else -10000

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
            value += piece_values[piece.piece_type] if piece.color == chess.WHITE else -piece_values[piece.piece_type]

        return value


def get_color(color: bool):
    return "white" if color==True else "black"
    
def init_game(current_date):
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
    logger.debug("Initializing app")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    board = chess.Board()
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('consolas', FONT_SIZE)
    images = load_images()
    game = chess.pgn.Game()
    node = game
    return screen, board, logger, clock, images, game, node, font

def load_images():
    images = {}
    pieces = ["king", "queen", "rook", "bishop", "knight", "pawn"]
    colors = ["white", "black"]
    for piece in pieces:
        for color in colors:
            img = pygame.image.load(f"assets/{piece}/{color}.png")
            img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
            images[f"{color}_{piece}"] = img
    images["white_square"] = pygame.image.load(f"assets/WhiteSquare.png")
    images["black_square"] = pygame.image.load(f"assets/BlackSquare.png")
    return images

def draw_piece(piece: chess.Piece, screen: pygame.Surface, pos: tuple[int, int], piece_images: Dict[str, pygame.Surface]):
    color = get_color(piece.color)
    type = chess.piece_name(piece.piece_type)
    x, y = pos
    x = x*SQUARE_SIZE
    y = y*SQUARE_SIZE
    img = piece_images[f"{color}_{type}"]

    screen.blit(img, (pos[0]*SQUARE_SIZE, pos[1]*SQUARE_SIZE))

def draw_square_overlay(screen: pygame.Surface, row: int, col: int, images: Dict[str, pygame.Surface]):
    if (row + col) % 2 == 1:
        screen.blit(images["black_square"], (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    else:
        screen.blit(images["white_square"], (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    pygame.draw.rect(screen, (128, 255, 128), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), width=15)

def draw_board(board: chess.Board, screen: pygame.Surface, players: tuple[Player, Player], images: Dict[str, pygame.Surface]):
    legal_moves = None
    screen.fill(EGGSHELL)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 1:
                screen.blit(images["black_square"], (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else:
                screen.blit(images["white_square"], (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    if board.turn == chess.WHITE:
        if players[0].selected_piece:
            row = 7 - chess.square_rank(players[0].selected_square)
            col = chess.square_file(players[0].selected_square)
            pygame.draw.rect(screen, (0, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            legal_moves = [move for move in board.legal_moves if move.from_square == players[0].selected_square]
    else:
        if players[1].selected_piece:
            row = 7 - chess.square_rank(players[1].selected_square)
            col = chess.square_file(players[1].selected_square)
            pygame.draw.rect(screen, (0, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            legal_moves = [move for move in board.legal_moves if move.from_square == players[1].selected_square]

    if legal_moves:    
        for move in legal_moves:
            row = 7 - chess.square_rank(move.to_square)
            col = chess.square_file(move.to_square)
            draw_square_overlay(screen, row, col, images)

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

def print_game_log(screen: pygame.Surface, font: pygame.font.Font, moves: tuple[chess.Move, ...]):
    if moves:
        x = FONT_SIZE + 5
        n = 1
        for move in moves:
            text = f"{n}. {move.uci()}"
            screen.blit(font.render(text, True, FONT_COLOR), (610,x))
            x += FONT_SIZE + 5
            n += 1

WIDTH, HEIGHT   = 1200, 600 # 600 x 600 herní pole
SQUARE_SIZE     = 600 // 8  # 75
ROWS, COLS      = 8, 8
WHITE           = (255, 255, 255)
MOSS_GREEN      = (119, 149, 86)
EGGSHELL        = (235, 236, 208)
BLACK           = (0, 0, 0)
FONT_COLOR      = BLACK
FONT_SIZE       = 30
