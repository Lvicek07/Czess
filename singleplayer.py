import pygame
from common import *
import logging as log
import chess
import chess.pgn
from os import chdir
from os.path import abspath, dirname
from datetime import datetime
from typing import Dict, Tuple
import random


class Player:
    def __init__(self, color: bool, board: chess.Board) -> None:
        self.is_playing = False
        self.clicked_piece = None
        self.color = color
        self.selected_piece = None
        self.selected_square = None
        self.board = board

    def on_move(self, events: tuple):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x = int(mouse_pos[0] // SQUARE_SIZE)
                y = 7 - int(mouse_pos[1] // SQUARE_SIZE)
                square = chess.square(x, y)
                piece = self.board.piece_at(square)

                if self.selected_piece:
                    if square == self.selected_square:
                        print("Cancelling move")
                        self.selected_piece = None
                        self.selected_square = None
                    elif piece and piece.color == self.color:
                        print("Cannot place piece on your own pieces")
                    else:
                        move = chess.Move(self.selected_square, square)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                            self.selected_piece = None
                            self.selected_square = None
                            print("Moved piece")
                        else:
                            print("Invalid move")
                elif piece:
                    if piece.color == self.color:
                        self.selected_piece = piece
                        self.selected_square = square
                        print("Piece selected")
                    else:
                        print("Selected enemy piece, cannot move")
                else:
                    print("No piece found")


class AI:
    def __init__(self, color: bool, difficulty: str):
        self.color = color
        self.difficulty = difficulty

    def get_move(self, board: chess.Board) -> chess.Move:
        if self.difficulty == "easy":
            return self.easy_move(board)
        elif self.difficulty == "medium":
            return self.medium_move(board)
        elif self.difficulty == "hard":
            return self.hard_move(board)
        elif self.difficulty == "Fales":
            return self.fales_move(board)

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

    def minimax(self, board: chess.Board, depth: int, maximizing_player: bool = True) -> Tuple[chess.Move, int]:
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


def init_game():
    return chess.Board()


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


def draw_piece(piece: chess.Piece, screen: pygame.Surface, pos: Tuple[int, int], piece_images: Dict[str, pygame.Surface]):
    color = "white" if piece.color == chess.WHITE else "black"
    type = chess.piece_name(piece.piece_type)
    x, y = pos
    img = piece_images[f"{color}_{type}"]
    screen.blit(img, (x * SQUARE_SIZE, y * SQUARE_SIZE))


def draw_board(board: chess.Board, screen: pygame.Surface, piece_images: Dict[str, pygame.Surface]):
    screen.fill((235, 236, 208))  # EGGSHELL
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 1:
                pygame.draw.rect(screen, (119, 149, 86), (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    for square, piece in board.piece_map().items():
        x = chess.square_file(square)
        y = chess.square_rank(square)
        draw_piece(piece, screen, (x, 7 - y), piece_images)


def draw_menu(screen: pygame.Surface):
    screen.fill((30, 30, 30))  # Dark background
    font = pygame.font.Font(None, 74)
    title_text = font.render("Select Difficulty", True, (255, 255, 255))
    screen.blit(title_text, (WIDTH // 4, HEIGHT // 4))

    button_font = pygame.font.Font(None, 48)
    difficulties = ["Easy", "Medium", "Hard", "Fales"]
    for i, difficulty in enumerate(difficulties):
        button_text = button_font.render(difficulty, True, (255, 255, 255))
        screen.blit(button_text, (WIDTH // 4, HEIGHT // 2 + i * 60))

    pygame.display.flip()


def main(current_date):
    global logger
    chdir(dirname(abspath(__file__)))
    logger = log.getLogger(__name__)
    log_filename = f"logs/log_{current_date}.log"
    log.basicConfig(filename=log_filename, filemode="a", level=log.DEBUG, format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

    pygame.init()
    global WIDTH, HEIGHT, SQUARE_SIZE
    WIDTH, HEIGHT = 600, 650
    SQUARE_SIZE = WIDTH // 8

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess Game')

    piece_images = load_images()

    # Show the menu for difficulty selection
    selected_difficulty = None
    while selected_difficulty is None:
        draw_menu(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                y = mouse_pos[1]
                if HEIGHT // 2 < y < HEIGHT // 2 + 240:  # Checking button area
                    index = (y - (HEIGHT // 2)) // 60
                    if 0 <= index < 4:
                        selected_difficulty = ["easy", "medium", "hard", "Fales"][index]

    board = init_game()
    player = Player(chess.WHITE, board)
    ai = AI(chess.BLACK, difficulty=selected_difficulty)  # Change difficulty as needed

    run = True
    while run:
        events = pygame.event.get()
        player.on_move(events)

        if board.turn == chess.BLACK:  # AI's turn
            move = ai.get_move(board)
            if move:
                board.push(move)

        draw_board(board, screen, piece_images)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    try:
        current_date = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        main(current_date)
        logger.info("Program exited")
    except Exception as e:
        logger.error(e)
        raise e

