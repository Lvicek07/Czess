import os
import base64

SQUARE_SIZE = 75

images = {}
pieces = ["king", "queen", "rook", "bishop", "knight", "pawn", "square"]
colors = ["white", "black"]

os.chdir(os.path.dirname(os.path.abspath(__file__)))

assets_dir = "assets"
for piece in pieces:
    for color in colors:
        img_path = os.path.join(assets_dir, piece, f"{color}.png")
        with open(img_path, "rb") as f:
            images[f"{color}_{piece}"] = base64.b64encode(f.read()).decode('utf-8')
img_path = os.path.join(assets_dir, "ChessBoard.png")
with open(img_path, "rb") as f:
    images["chess_board"] = base64.b64encode(f.read()).decode('utf-8')
with open("images_b64.txt", "w") as f:
    for key, value in images.items():
        f.write(f"\t'{key}': '{value}',\n")
    