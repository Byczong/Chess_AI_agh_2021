"""Main driver file - visualization and user interaction"""

import pygame as p

import Engine

"""Global variables/constants concerning visualization"""
PIECES = {}
CHESSBOARD_WIDTH, CHESSBOARD_HEIGHT = 512, 512
BORDER_WIDTH = 32
WIDTH, HEIGHT = CHESSBOARD_WIDTH + BORDER_WIDTH, CHESSBOARD_HEIGHT + BORDER_WIDTH
SCREEN = p.display.set_mode((WIDTH, HEIGHT))
SQUARE_SIZE = CHESSBOARD_HEIGHT // 8
FPS = 30


COLOR_LIGHT = p.Color((255, 235, 205))
COLOR_DARK = p.Color((140, 80, 42))
COLOR_HIGHLIGHT = p.Color((218, 112, 214))

BOARD_RANKS = ['1', '2', '3', '4', '5', '6', '7', '8']
BOARD_FILES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


def main():
    p.init()
    p.display.set_caption("Chess (Alpha-Beta testing)")
    clock = p.time.Clock()
    SCREEN.fill(COLOR_DARK)
    load_pieces()
    chessboard_state = Engine.ChessboardState()
    running = True
    selected_tile = ()
    selected_piece = None
    possible_moves = []
    tiles_clicked_on = []

    def reset_move_attempt():
        nonlocal selected_tile, selected_piece, possible_moves, tiles_clicked_on
        selected_tile = ()
        tiles_clicked_on = []
        selected_piece = None
        possible_moves = []

    while running:
        clock.tick(FPS)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                position = p.mouse.get_pos()

                # Right click
                if event.button == 3:
                    reset_move_attempt()

                # Middle click
                elif event.button == 2:
                    reset_move_attempt()
                    # TODO: Undo the last move

                # Left click
                if event.button == 1 and position[0] <= CHESSBOARD_WIDTH and position[1] <= CHESSBOARD_HEIGHT:
                    mouse_row = position[1] // SQUARE_SIZE
                    mouse_col = position[0] // SQUARE_SIZE
                    print(f"Clicked on {get_tile_str((mouse_row, mouse_col))}")

                    # Double click
                    if selected_tile == (mouse_row, mouse_col):
                        reset_move_attempt()
                    else:
                        selected_tile = (mouse_row, mouse_col)
                        tiles_clicked_on.append(selected_tile)

                        # First position selected v1
                        if len(tiles_clicked_on) == 1:
                            selected_piece = chessboard_state.board[mouse_row][mouse_col]
                            if selected_piece is not None:
                                possible_moves = get_legal_moves_list(selected_piece)
                                print_possible_moves(possible_moves)
                                if possible_moves is None:
                                    reset_move_attempt()
                            else:
                                reset_move_attempt()

                        # Second position selected
                        elif len(tiles_clicked_on) == 2:
                            if list(selected_tile) in possible_moves:
                                chessboard_state.board[tiles_clicked_on[0][0]][tiles_clicked_on[0][1]] \
                                    .move(tiles_clicked_on[1])

                                if (chessboard_state.game_state() == Engine.GameState.CHECK):
                                        print("Check!")
                                elif (chessboard_state.game_state() == Engine.GameState.CHECKMATE):
                                    print("Checkmate!")
                                elif (chessboard_state.game_state() == Engine.GameState.STALEMATE):
                                    print("Stalemate!")
                                elif (chessboard_state.game_state() == Engine.GameState.CONTINUE):
                                    print("Continue!")

                                # TODO: Cool sound when taking pieces, less cool when not
                                reset_move_attempt()
                            # First position selected v2
                            else:
                                tiles_clicked_on = [selected_tile]
                                selected_piece = chessboard_state.board[mouse_row][mouse_col]
                                if selected_piece is not None:
                                    possible_moves = get_legal_moves_list(selected_piece)
                                    print_possible_moves(possible_moves)
                                    if possible_moves is None:
                                        reset_move_attempt()
                                else:
                                    reset_move_attempt()

        draw_chessboard_state(chessboard_state, selected_tile, possible_moves)
        p.display.flip()


# Allow accessing a piece's image by PIECE['c#'], where c - color, # - abr. piece's name
def load_pieces():
    """Load piece's images from "pieces" folder"""
    pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
    for piece in pieces:
        PIECES[piece] = p.transform.scale(p.image.load("pieces/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def draw_chessboard_state(chessboard_state, selected_tile, possible_moves):
    """Show the game"""
    draw_chessboard()
    highlight_possible_moves(selected_tile, possible_moves, chessboard_state)
    draw_pieces(chessboard_state)
    # TODO: Highlight check


def draw_chessboard():
    """Draw the squares on the board along with the border describing ranks and files"""
    for row in range(8):
        for col in range(8):
            p.draw.rect(SCREEN, get_tile_color(row, col),
                        p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    p.draw.line(SCREEN, p.Color(173, 116, 59), (8 * SQUARE_SIZE, 0), (8 * SQUARE_SIZE, 8 * SQUARE_SIZE), width=3)
    p.draw.line(SCREEN, p.Color(173, 116, 59), (0, 8 * SQUARE_SIZE), (8 * SQUARE_SIZE, 8 * SQUARE_SIZE), width=3)
    font = p.font.SysFont("monospace", 24)
    for row in range(8):
        label = font.render(get_rank(row), True, COLOR_LIGHT)
        SCREEN.blit(label, (8 * SQUARE_SIZE + BORDER_WIDTH // 3, row * SQUARE_SIZE + SQUARE_SIZE // 3))
    for col in range(8):
        label = font.render(get_file(col), True, COLOR_LIGHT)
        SCREEN.blit(label, (col * SQUARE_SIZE + SQUARE_SIZE // 3 + 4, 8 * SQUARE_SIZE + BORDER_WIDTH // 6))


def highlight_possible_moves(selected_tile, possible_moves, chessboard_state):
    """Highlight all the possible moves along with the selected tile"""
    if selected_tile == ():
        return

    p.draw.rect(SCREEN, COLOR_HIGHLIGHT,
                p.Rect(selected_tile[1] * SQUARE_SIZE, selected_tile[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    for pos in possible_moves:
        if chessboard_state.board[pos[0]][pos[1]] is None:
            p.draw.circle(SCREEN, COLOR_HIGHLIGHT,
                          (pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2, pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2),
                          SQUARE_SIZE // 5)
        else:
            p.draw.rect(SCREEN, COLOR_HIGHLIGHT,
                        p.Rect(pos[1] * SQUARE_SIZE, pos[0] * SQUARE_SIZE, SQUARE_SIZE,
                               SQUARE_SIZE))


def draw_pieces(chessboard_state):
    """Draw pieces on the board"""
    for row in range(8):
        for col in range(8):
            piece = chessboard_state.board[row][col]
            if piece is not None:
                SCREEN.blit(PIECES[str(piece)],
                            p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def get_legal_moves_list(piece):
    """Get list() of legal move generator (if color is wrong or piece is None return None)"""
    if piece is not None:
        return piece.get_legal_moves_list()
    else:
        return None

def get_rank(n):
    """Get rank string from ChessboardState.board index"""
    return BOARD_RANKS[7 - n]

def get_file(n):
    """Get file string from ChessboardState.board index"""
    return BOARD_FILES[n]

def get_tile_str(pos):
    """Get tile string from ChessboardState.board indices"""
    return get_file(pos[1]) + get_rank(pos[0])

def get_tile_color(row, column):
    """Get tile's color from ChessboardState.board index"""
    return COLOR_LIGHT if (row + column) % 2 == 0 else COLOR_DARK

def print_possible_moves(possible_moves):
    """Print possible moves"""
    if possible_moves is None:
        print(f"No moves possible")
    else:
        print(f"Possible moves: {[get_tile_str(tuple(move)) for move in possible_moves]}")

if __name__ == '__main__':
    main()

# Side notes:
# - To update requirements: pip freeze > requirements.txt in console.
