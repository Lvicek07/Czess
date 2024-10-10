import chess
from keyboard import play
import pygame
from time import time
from typing import Dict
from pygame import Color

class Player:
    def __init__(self, color: bool, board: chess.Board) -> None:
        self.is_playing      = False
        self.clicked_piece   = None
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


def get_color(color: bool):
    return "white" if color==True else "black"
    
def init_game():
    board = chess.Board()
    return board

def load_images():
    piece_images = {}
    pieces = ["king", "queen", "rook", "bishop", "knight", "pawn"]
    colors = ["white", "black"]
    for piece in pieces:
        for color in colors:
            img = pygame.image.load(f"assets/{piece}/{color}.png")
            img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
            piece_images[f"{color}_{piece}"] = img
    return piece_images

def draw_piece(piece: chess.Piece, screen: pygame.Surface, pos: tuple[int, int], piece_images: Dict[str, pygame.Surface]):
    color = get_color(piece.color)
    type = chess.piece_name(piece.piece_type)
    x, y = pos
    x = x*SQUARE_SIZE
    y = y*SQUARE_SIZE
    img = piece_images[f"{color}_{type}"]

    screen.blit(img, (pos[0]*SQUARE_SIZE, pos[1]*SQUARE_SIZE))

def draw_board(board: chess.Board, screen: pygame.Surface, players: tuple[Player, Player], piece_images: Dict[str, pygame.Surface]):
    img = pygame.image.load(f"assets/WhiteSquare.png")
    screen.fill(EGGSHELL)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 1:
                pygame.draw.rect(screen, MOSS_GREEN, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            else:
                screen.blit(img, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    if board.turn == chess.WHITE:
        if players[0].selected_piece:
            row = 7 - chess.square_rank(players[0].selected_square)
            col = chess.square_file(players[0].selected_square)
            pygame.draw.rect(screen, (0, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            legal_moves = [move for move in board.legal_moves if move.from_square == players[0].selected_square]
            for move in legal_moves:
                row = 7 - chess.square_rank(move.to_square)
                col = chess.square_file(move.to_square)
                pygame.draw.rect(screen, (128, 255, 128), (col * SQUARE_SIZE + SQUARE_SIZE//4, row * SQUARE_SIZE + SQUARE_SIZE//4, SQUARE_SIZE - SQUARE_SIZE//2, SQUARE_SIZE - SQUARE_SIZE//2))
    else:
        if players[1].selected_piece:
            row = 7 - chess.square_rank(players[1].selected_square)
            col = chess.square_file(players[1].selected_square)
            pygame.draw.rect(screen, (0, 255, 0), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            legal_moves = [move for move in board.legal_moves if move.from_square == players[1].selected_square]
            for move in legal_moves:
                row = 7 - chess.square_rank(move.to_square)
                col = chess.square_file(move.to_square)
                pygame.draw.rect(screen, (128, 255, 128), (col * SQUARE_SIZE + SQUARE_SIZE//4, row * SQUARE_SIZE + SQUARE_SIZE//4, SQUARE_SIZE - SQUARE_SIZE//2, SQUARE_SIZE - SQUARE_SIZE//2))

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
            draw_piece(piece, screen, (x, y), piece_images)
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
