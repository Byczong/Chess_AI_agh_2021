# Main driver file - visualization and user interaction

import pygame as p

import Engine

# Global variables/constants concerning visualization
PIECES = {}
WIDTH, HEIGHT = 512, 512
SCREEN = p.display.set_mode((WIDTH, HEIGHT))
SQUARE_SIZE = HEIGHT // 8
FPS = 30


def main():
    p.init()
    clock = p.time.Clock()
    SCREEN.fill(p.Color("white"))
    load_pieces()
    chessboard_state = Engine.ChessboardState()
    run = True
    while run:
        clock.tick(FPS)
        for event in p.event.get():
            if event.type == p.QUIT:
                run = False
        draw_chessboard_state(chessboard_state)
        p.display.flip()


# Load piece's images from "pieces" folder
# Allow accessing a piece's image by PIECE['c#'], where c - color, # - abr. piece's name
def load_pieces():
    pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
    for piece in pieces:
        PIECES[piece] = p.transform.scale(p.image.load("pieces/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

# Show the game
def draw_chessboard_state(chessboard_state):
    draw_chessboard()
    draw_pieces(chessboard_state)
    # TODO: Implement drawing procedures

# Draw the squares on the board
def draw_chessboard():
    pass

# Draw pieces on the board
def draw_pieces(chessboard_state):
    pass

if __name__ == '__main__':
    main()

# Side notes:
# - To update requirements: pip freeze > requirements.txt in console.
