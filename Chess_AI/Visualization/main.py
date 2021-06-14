"""Main driver file - visualization and user interaction"""

import pygame as p
import threading

import Chess_AI.Engine.Chessboard as chessboard
import Chess_AI.Engine.AI as ai

"""Global variables/constants concerning visualization"""
PIECES = {}
CHESSBOARD_WIDTH, CHESSBOARD_HEIGHT = 512, 512
BORDER_WIDTH = 32
WIDTH, HEIGHT = CHESSBOARD_WIDTH + BORDER_WIDTH, CHESSBOARD_HEIGHT + BORDER_WIDTH
SCREEN = p.display.set_mode((WIDTH, HEIGHT))
SQUARE_SIZE = CHESSBOARD_HEIGHT // 8
FPS = 12

BUTTON_WIDTH, BUTTON_HEIGHT = WIDTH // 3, HEIGHT // 8
BUTTONS_X = (WIDTH // 2 - BUTTON_WIDTH // 2, WIDTH // 2 + BUTTON_WIDTH // 2)
BUTTON_1_Y = (HEIGHT // 8 - BUTTON_HEIGHT // 2, HEIGHT // 8 + BUTTON_HEIGHT // 2)
BUTTON_2_Y = (HEIGHT // 8 - BUTTON_HEIGHT // 2 + HEIGHT // 4, HEIGHT // 8 + BUTTON_HEIGHT // 2 + HEIGHT // 4)
BUTTON_3_Y = (HEIGHT // 8 - BUTTON_HEIGHT // 2 + HEIGHT // 2, HEIGHT // 8 + BUTTON_HEIGHT // 2 + HEIGHT // 2)
BUTTON_4_Y = (HEIGHT // 8 - BUTTON_HEIGHT // 2 + 3 * HEIGHT // 4, HEIGHT // 8 + BUTTON_HEIGHT // 2 + 3 * HEIGHT // 4)

RECT_COLORS_WIDTH, RECT_COLORS_HEIGHT = WIDTH // 16, (BUTTON_3_Y[1] - BUTTON_3_Y[0]) // 2
RECT_COLOR_A_X = (BUTTONS_X[1] + WIDTH // 32, BUTTONS_X[1] + WIDTH // 32 + RECT_COLORS_WIDTH)
RECT_COLOR_A_Y = (BUTTON_3_Y[0], BUTTON_3_Y[0] + RECT_COLORS_HEIGHT)
RECT_COLOR_B_X = (BUTTONS_X[1] + WIDTH // 32, BUTTONS_X[1] + WIDTH // 32 + RECT_COLORS_WIDTH)
RECT_COLOR_B_Y = (RECT_COLOR_A_Y[1], RECT_COLOR_A_Y[1] + RECT_COLORS_HEIGHT)

RECT_GAME_END_WIDTH, RECT_GAME_END_HEIGHT = WIDTH // 2, HEIGHT // 2
RECT_GAME_END_X = (WIDTH // 4, WIDTH // 4 + RECT_GAME_END_WIDTH)
RECT_GAME_END_Y = (HEIGHT // 4, HEIGHT // 4 + RECT_GAME_END_HEIGHT)

BUTTON_CLOSE_POPUP_X = (WIDTH // 2 - BUTTON_WIDTH // 2, WIDTH // 2 + BUTTON_WIDTH // 2)
BUTTON_CLOSE_POPUP_Y = (HEIGHT // 8 - BUTTON_HEIGHT // 2 + HEIGHT // 2, HEIGHT // 8 + BUTTON_HEIGHT // 2 + HEIGHT // 2)

COLOR_LIGHT = p.Color((255, 235, 205))
COLOR_DARK = p.Color((140, 80, 42))
COLOR_HIGHLIGHT = p.Color((53, 180, 159))
COLOR_CHECK = p.Color((200, 40, 65))
COLOR_STALEMATE = p.Color((50, 180, 57))
COLOR_BORDER = p.Color(173, 116, 59)

BOARD_RANKS = ['1', '2', '3', '4', '5', '6', '7', '8']
BOARD_FILES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


class ThreadAI(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        if kwargs is None:
            kwargs = {}
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return


def main():
    p.init()
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    SCREEN.fill(COLOR_DARK)
    load_pieces()
    running = True
    quit_after_loop = False
    selected_tile = None
    selected_piece = None
    possible_moves = []
    tiles_clicked_on = []
    king_pos = None
    player_is_white = True
    first_white_ai_move_made = False
    view_promotion_box = False
    promotion_choice = None
    view_ending_box = False
    white_won = None
    end_state = None

    chessboard_state = chessboard.ChessboardState()
    play_against_ai = False

    def reset_move_attempt():
        nonlocal selected_tile, selected_piece, possible_moves, tiles_clicked_on, promotion_choice
        selected_tile = None
        tiles_clicked_on = []
        selected_piece = None
        possible_moves = []
        promotion_choice = None

    def init_game(is_fist_init):
        nonlocal running, quit_after_loop, play_against_ai, position, view_ending_box, white_won, player_is_white, \
            view_promotion_box, promotion_choice, chessboard_state, first_white_ai_move_made, selected_tile, end_state
        while running:
            clock.tick(FPS)
            for e in p.event.get():
                if e.type == p.QUIT:
                    quit_after_loop = True
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    if e.button == 1:
                        position = p.mouse.get_pos()
                        if BUTTONS_X[0] <= position[0] <= BUTTONS_X[1]:
                            if BUTTON_1_Y[0] <= position[1] <= BUTTON_1_Y[1]:
                                running = False
                                play_against_ai = False
                            elif BUTTON_2_Y[0] <= position[1] <= BUTTON_2_Y[1]:
                                running = False
                                play_against_ai = True
                            elif BUTTON_3_Y[0] <= position[1] <= BUTTON_3_Y[1]:
                                player_is_white = not player_is_white

                            elif BUTTON_4_Y[0] <= position[1] <= BUTTON_4_Y[1]:
                                quit_after_loop = True
                                running = False
            draw_init_window(player_is_white)
            p.display.flip()

        if quit_after_loop and is_fist_init:
            p.quit()
        elif quit_after_loop:
            running = False
        else:
            running = True
            SCREEN.fill(COLOR_DARK)
            first_white_ai_move_made = False
            selected_tile = None
            view_ending_box = False
            view_promotion_box = False
            promotion_choice = None
            white_won = None
            end_state = None
            chessboard_state = chessboard.ChessboardState()

    def make_ai_move():
        nonlocal chessboard_state, king_pos, view_ending_box, white_won, end_state

        ai_thread = ThreadAI(target=ai.ChessAI(chessboard_state).ai_move, args=(3,))
        ai_thread.start()

        while ai_thread.is_alive():
            clock.tick(FPS)

        ai_move = ai_thread.join()

        if ai_move is None:
            return
        chessboard_state.board[ai_move[0][0]][ai_move[0][1]].move(ai_move[1])
        king_pos = chessboard_state.white_king.position if chessboard_state.white_to_move \
            else chessboard_state.black_king.position
        draw_chessboard_state(chessboard_state, selected_tile, possible_moves, king_pos, view_promotion_box=False)
        p.display.flip()

        print(f"[AIMove]: {get_tile_str(ai_move[0])} --> {get_tile_str(ai_move[1])}")
        if chessboard_state.game_state() == chessboard.GameState.CHECK:
            print("[GameState]: Check")
        elif chessboard_state.game_state() == chessboard.GameState.CHECKMATE:
            print("[GameState]: Checkmate")
            view_ending_box = True
            white_won = not chessboard_state.white_to_move
            end_state = chessboard.GameState.CHECKMATE
        elif chessboard_state.game_state() == chessboard.GameState.STALEMATE:
            print("[GameState]: Stalemate")
            view_ending_box = True
            white_won = None
            end_state = chessboard.GameState.STALEMATE
        elif chessboard_state.game_state() == chessboard.GameState.CONTINUE:
            print("[GameState]: Continue")
        elif chessboard_state.game_state() == chessboard.GameState.INSUFFICIENT_MATERIAL:
            print("[GameState]: Insufficient material")
            view_ending_box = True
            white_won = None
            end_state = chessboard.GameState.INSUFFICIENT_MATERIAL

    # Initial window
    init_game(True)

    # Main window
    while running:
        clock.tick(FPS)
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

            elif event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    print("------------")
                    print("Go back to the menu")
                    init_game(False)

            if play_against_ai and not player_is_white and not first_white_ai_move_made:
                make_ai_move()
                first_white_ai_move_made = True

            elif event.type == p.MOUSEBUTTONDOWN:
                position = p.mouse.get_pos()

                # Right click
                if not view_ending_box and not view_promotion_box and event.button == 3:
                    reset_move_attempt()

                # Middle click
                elif not view_ending_box and not view_promotion_box and event.button == 2:
                    reset_move_attempt()
                    # Undo move
                    if play_against_ai:
                        if (chessboard_state.game_state() == chessboard.GameState.CHECKMATE or
                                chessboard_state.game_state() == chessboard.GameState.STALEMATE or
                                chessboard_state.game_state() == chessboard.GameState.INSUFFICIENT_MATERIAL) and \
                                player_is_white != chessboard_state.white_to_move:
                            chessboard_state.undo_move()
                        else:
                            chessboard_state.undo_move()
                            chessboard_state.undo_move()
                    else:
                        chessboard_state.undo_move()
                    king_pos = chessboard_state.white_king.position if chessboard_state.white_to_move \
                        else chessboard_state.black_king.position

                # Promotion choice left click
                if view_promotion_box:
                    top_tile = tuple(selected_tile) if chessboard_state.white_to_move else (4, selected_tile[1])
                    top_left_coords = (top_tile[1] * SQUARE_SIZE, top_tile[0] * SQUARE_SIZE)
                    top_right_coords = (top_tile[1] * SQUARE_SIZE + SQUARE_SIZE, top_tile[0] * SQUARE_SIZE)
                    bottom_left_coords = (top_tile[1] * SQUARE_SIZE, top_tile[0] * SQUARE_SIZE + 4 * SQUARE_SIZE)
                    if event.button == 1 and top_left_coords[0] <= position[0] <= top_right_coords[0] and \
                            top_left_coords[1] <= position[1] <= bottom_left_coords[1]:

                        if top_left_coords[1] <= position[1] <= top_left_coords[1] + SQUARE_SIZE:
                            promotion_choice = chessboard.Queen
                        elif top_left_coords[1] + SQUARE_SIZE <= position[1] <= top_left_coords[1] + 2 * SQUARE_SIZE:
                            promotion_choice = chessboard.Knight
                        elif top_left_coords[1] + 2 * SQUARE_SIZE <= position[1] \
                                <= top_left_coords[1] + 3 * SQUARE_SIZE:
                            promotion_choice = chessboard.Rook
                        elif top_left_coords[1] + 3 * SQUARE_SIZE <= position[1] <= bottom_left_coords[1]:
                            promotion_choice = chessboard.Bishop
                        else:
                            promotion_choice = chessboard.Queen

                        chessboard_state.board[tiles_clicked_on[0][0]][tiles_clicked_on[0][1]] \
                            .move(tiles_clicked_on[1], promotion_choice=promotion_choice)

                        king_pos = chessboard_state.white_king.position if chessboard_state.white_to_move \
                            else chessboard_state.black_king.position

                        view_promotion_box = False
                        reset_move_attempt()
                    else:
                        view_promotion_box = False
                        reset_move_attempt()

                # Popup left click
                if view_ending_box:
                    if event.button == 1:
                        if BUTTON_CLOSE_POPUP_X[0] <= position[0] <= BUTTON_CLOSE_POPUP_X[1]:
                            if BUTTON_CLOSE_POPUP_Y[0] <= position[1] <= BUTTON_CLOSE_POPUP_Y[1]:
                                # Close popup
                                view_ending_box = False
                                white_won = None
                                end_state = None

                # Left click
                if not view_ending_box and not view_promotion_box and event.button == 1 and \
                        position[0] <= CHESSBOARD_WIDTH and position[1] <= CHESSBOARD_HEIGHT:
                    mouse_row = position[1] // SQUARE_SIZE
                    mouse_col = position[0] // SQUARE_SIZE
                    print(f"Clicked on {get_tile_str((mouse_row, mouse_col))}")

                    # Double click
                    if selected_tile == [mouse_row, mouse_col]:
                        reset_move_attempt()
                    else:
                        selected_tile = [mouse_row, mouse_col]
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
                            if selected_tile in possible_moves:
                                if isinstance(selected_piece, chessboard.Pawn) and selected_tile[0] in [0, 7]:
                                    # View promotion box
                                    view_promotion_box = True
                                else:
                                    chessboard_state.board[tiles_clicked_on[0][0]][tiles_clicked_on[0][1]] \
                                        .move(tiles_clicked_on[1])

                                king_pos = chessboard_state.white_king.position if chessboard_state.white_to_move \
                                    else chessboard_state.black_king.position

                                if not view_promotion_box:
                                    print(f"[HumanMove]: {get_tile_str(tiles_clicked_on[0])} -->"
                                          f" {get_tile_str(tiles_clicked_on[1])}")
                                    if chessboard_state.game_state() == chessboard.GameState.CHECK:
                                        print("[GameState]: Check")
                                    elif chessboard_state.game_state() == chessboard.GameState.CHECKMATE:
                                        print("[GameState]: Checkmate")
                                        view_ending_box = True
                                        white_won = not chessboard_state.white_to_move
                                        end_state = chessboard.GameState.CHECKMATE
                                    elif chessboard_state.game_state() == chessboard.GameState.STALEMATE:
                                        print("[GameState]: Stalemate")
                                        view_ending_box = True
                                        white_won = None
                                        end_state = chessboard.GameState.STALEMATE
                                    elif chessboard_state.game_state() == chessboard.GameState.CONTINUE:
                                        print("[GameState]: Continue")
                                    elif chessboard_state.game_state() == chessboard.GameState.INSUFFICIENT_MATERIAL:
                                        print("[GameState]: Insufficient material")
                                        view_ending_box = True
                                        white_won = None
                                        end_state = chessboard.GameState.INSUFFICIENT_MATERIAL
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

        draw_chessboard_state(chessboard_state, selected_tile, possible_moves, king_pos, view_promotion_box)
        if view_promotion_box:
            draw_promotion_choice(selected_tile, white_move=chessboard_state.white_to_move)
        if view_ending_box:
            draw_game_ending(end_state, white_won)
        p.display.flip()

        if play_against_ai and (player_is_white != chessboard_state.white_to_move):
            make_ai_move()


# Allow accessing a piece's image by PIECE['c#'], where c - color, # - abr. piece's name
def load_pieces():
    """Load piece's images from "pieces" folder"""
    pieces = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
    for piece in pieces:
        PIECES[piece] = p.transform.scale(p.image.load("../pieces/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def draw_chessboard_state(chessboard_state, selected_tile, possible_moves, king_pos, view_promotion_box):
    """Draw the game"""
    draw_chessboard()
    if king_pos is not None:
        highlight_king(chessboard_state, king_pos)
    if not view_promotion_box:
        highlight_possible_moves(selected_tile, possible_moves, chessboard_state)
    draw_pieces(chessboard_state)


def draw_chessboard():
    """Draw the tiles on the board along with the border describing ranks and files"""
    for row in range(8):
        for col in range(8):
            p.draw.rect(SCREEN, get_tile_color(row, col),
                        p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    p.draw.line(SCREEN, COLOR_BORDER, (8 * SQUARE_SIZE, 0), (8 * SQUARE_SIZE, 8 * SQUARE_SIZE), width=3)
    p.draw.line(SCREEN, COLOR_BORDER, (0, 8 * SQUARE_SIZE), (8 * SQUARE_SIZE, 8 * SQUARE_SIZE), width=3)
    font = p.font.SysFont("monospace", 24)
    for row in range(8):
        label = font.render(get_rank(row), True, COLOR_LIGHT)
        SCREEN.blit(label, (8 * SQUARE_SIZE + BORDER_WIDTH // 3, row * SQUARE_SIZE + SQUARE_SIZE // 3))
    for col in range(8):
        label = font.render(get_file(col), True, COLOR_LIGHT)
        SCREEN.blit(label, (col * SQUARE_SIZE + SQUARE_SIZE // 3 + 4, 8 * SQUARE_SIZE + BORDER_WIDTH // 6))


def highlight_possible_moves(selected_tile, possible_moves, chessboard_state):
    """Highlight all the possible moves along with the selected tile"""
    if selected_tile is None:
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


def highlight_king(chessboard_state, king_pos):
    """Highlight appropriate king that is being checked, checkmated or stalemated"""
    if chessboard_state.game_state() == chessboard.GameState.CHECK:
        p.draw.rect(SCREEN, COLOR_CHECK,
                    p.Rect(king_pos[1] * SQUARE_SIZE, king_pos[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.draw.circle(SCREEN, get_tile_color(king_pos[0], king_pos[1]),
                      (king_pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2, king_pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2),
                      SQUARE_SIZE // 2)

    elif chessboard_state.game_state() == chessboard.GameState.CHECKMATE:
        p.draw.rect(SCREEN, COLOR_CHECK,
                    p.Rect(king_pos[1] * SQUARE_SIZE, king_pos[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    elif chessboard_state.game_state() == chessboard.GameState.STALEMATE:
        p.draw.rect(SCREEN, COLOR_STALEMATE,
                    p.Rect(king_pos[1] * SQUARE_SIZE, king_pos[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.draw.circle(SCREEN, get_tile_color(king_pos[0], king_pos[1]),
                      (king_pos[1] * SQUARE_SIZE + SQUARE_SIZE // 2, king_pos[0] * SQUARE_SIZE + SQUARE_SIZE // 2),
                      SQUARE_SIZE // 2)


def draw_pieces(chessboard_state):
    """Draw pieces on the board"""
    for row in range(8):
        for col in range(8):
            piece = chessboard_state.board[row][col]
            if piece is not None:
                SCREEN.blit(PIECES[str(piece)],
                            p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_init_window(top_is_white=True):
    """Draw initial window with buttons"""
    SCREEN.fill(COLOR_LIGHT)
    texts = ["Play alone", "Play against AI", "Swap colors", "Quit"]
    font = p.font.SysFont("monospace", 18)
    labels = [font.render(text, True, COLOR_LIGHT) for text in texts]
    labels_rects = [labels[0].get_rect(center=(WIDTH // 2, HEIGHT // 8)),
                    labels[1].get_rect(center=(WIDTH // 2, 3 * HEIGHT // 8)),
                    labels[2].get_rect(center=(WIDTH // 2, 5 * HEIGHT // 8)),
                    labels[3].get_rect(center=(WIDTH // 2, 7 * HEIGHT // 8))]

    swap_colors_texts = ["You", "AI"]
    swap_colors_labels = [font.render(text, True, p.Color(119, 136, 153)) for text in swap_colors_texts]
    swap_colors_labels_rects = [swap_colors_labels[0].get_rect(center=((RECT_COLOR_A_X[0] + RECT_COLOR_A_X[1]) // 2,
                                                                       (RECT_COLOR_A_Y[0] + RECT_COLOR_A_Y[1]) // 2)),
                                swap_colors_labels[1].get_rect(center=((RECT_COLOR_B_X[0] + RECT_COLOR_B_X[1]) // 2,
                                                                       (RECT_COLOR_B_Y[0] + RECT_COLOR_B_Y[1]) // 2))]

    p.draw.rect(SCREEN, COLOR_DARK, p.Rect(BUTTONS_X[0], BUTTON_1_Y[0], BUTTON_WIDTH, BUTTON_HEIGHT))
    SCREEN.blit(labels[0], labels_rects[0])

    p.draw.rect(SCREEN, COLOR_DARK, p.Rect(BUTTONS_X[0], BUTTON_2_Y[0], BUTTON_WIDTH, BUTTON_HEIGHT))
    SCREEN.blit(labels[1], labels_rects[1])

    p.draw.rect(SCREEN, COLOR_DARK, p.Rect(BUTTONS_X[0], BUTTON_3_Y[0], BUTTON_WIDTH, BUTTON_HEIGHT))
    SCREEN.blit(labels[2], labels_rects[2])

    if top_is_white:
        p.draw.rect(SCREEN, p.Color(255, 255, 255), p.Rect(RECT_COLOR_A_X[0], RECT_COLOR_A_Y[0],
                                                           RECT_COLORS_WIDTH, RECT_COLORS_HEIGHT))
        p.draw.rect(SCREEN, p.Color(0, 0, 0), p.Rect(RECT_COLOR_B_X[0], RECT_COLOR_B_Y[0],
                                                     RECT_COLORS_WIDTH, RECT_COLORS_HEIGHT))
    else:
        p.draw.rect(SCREEN, p.Color(0, 0, 0), p.Rect(RECT_COLOR_A_X[0], RECT_COLOR_A_Y[0],
                                                     RECT_COLORS_WIDTH, RECT_COLORS_HEIGHT))
        p.draw.rect(SCREEN, p.Color(255, 255, 255), p.Rect(RECT_COLOR_B_X[0], RECT_COLOR_B_Y[0],
                                                           RECT_COLORS_WIDTH, RECT_COLORS_HEIGHT))

    SCREEN.blit(swap_colors_labels[0], swap_colors_labels_rects[0])
    SCREEN.blit(swap_colors_labels[1], swap_colors_labels_rects[1])

    p.draw.line(SCREEN, COLOR_BORDER, (RECT_COLOR_A_X[0], RECT_COLOR_A_Y[0]),
                (RECT_COLOR_A_X[1], RECT_COLOR_A_Y[0]), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (RECT_COLOR_B_X[0], RECT_COLOR_B_Y[1]),
                (RECT_COLOR_B_X[1], RECT_COLOR_B_Y[1]), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (RECT_COLOR_A_X[0], RECT_COLOR_A_Y[0]),
                (RECT_COLOR_A_X[0], RECT_COLOR_B_Y[1]), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (RECT_COLOR_A_X[1], RECT_COLOR_A_Y[0]),
                (RECT_COLOR_A_X[1], RECT_COLOR_B_Y[1]), width=2)

    p.draw.rect(SCREEN, COLOR_DARK, p.Rect(BUTTONS_X[0], BUTTON_4_Y[0], BUTTON_WIDTH, BUTTON_HEIGHT))
    SCREEN.blit(labels[3], labels_rects[3])


def draw_game_ending(state, white_wins=None):
    p.draw.rect(SCREEN, COLOR_LIGHT, p.Rect(RECT_GAME_END_X[0], RECT_GAME_END_Y[0],
                                            RECT_GAME_END_WIDTH, RECT_GAME_END_HEIGHT))
    font = p.font.SysFont("monospace", 20)
    if white_wins is not None:
        top_text = "Winner: "
        top_text += "white" if white_wins else "black"
        label = font.render(top_text, True, COLOR_DARK)
        label_rect = label.get_rect(center=(((RECT_GAME_END_X[0] + RECT_GAME_END_X[1]) // 2),
                                            (RECT_GAME_END_Y[0] + (RECT_GAME_END_Y[0] + RECT_GAME_END_Y[1]) // 2) // 2))
        SCREEN.blit(label, label_rect)
    else:
        top_text = "Draw!"
        label = font.render(top_text, True, COLOR_DARK)
        label_rect = label.get_rect(center=(((RECT_GAME_END_X[0] + RECT_GAME_END_X[1]) // 2),
                                            (RECT_GAME_END_Y[0] + (RECT_GAME_END_Y[0] + RECT_GAME_END_Y[1]) // 2) // 2))
        SCREEN.blit(label, label_rect)

    bottom_text = "State: "
    if state == chessboard.GameState.STALEMATE:
        bottom_text += "Stalemate"
    elif state == chessboard.GameState.INSUFFICIENT_MATERIAL:
        bottom_text += "Too few pieces"
    elif state == chessboard.GameState.CHECKMATE:
        bottom_text += "Checkmate"
    label = font.render(bottom_text, True, COLOR_DARK)
    label_rect = label.get_rect(center=(((RECT_GAME_END_X[0] + RECT_GAME_END_X[1]) // 2),
                                        (RECT_GAME_END_Y[0] + RECT_GAME_END_Y[1]) // 2))
    SCREEN.blit(label, label_rect)

    p.draw.line(SCREEN, COLOR_BORDER, (BUTTONS_X[0], BUTTON_3_Y[0]),
                (BUTTONS_X[1], BUTTON_3_Y[0]), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (BUTTONS_X[0], BUTTON_3_Y[1]),
                (BUTTONS_X[1], BUTTON_3_Y[1]), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (BUTTONS_X[1], BUTTON_3_Y[0]),
                (BUTTONS_X[1], BUTTON_3_Y[1]), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (BUTTONS_X[0], BUTTON_3_Y[0]),
                (BUTTONS_X[0], BUTTON_3_Y[1]), width=2)

    label = font.render("Close", True, COLOR_DARK)
    label_rect = label.get_rect(center=(((RECT_GAME_END_X[0] + RECT_GAME_END_X[1]) // 2),
                                        (RECT_GAME_END_Y[1] + (RECT_GAME_END_Y[0] + RECT_GAME_END_Y[1]) // 2) // 2))
    SCREEN.blit(label, label_rect)

    p.draw.line(SCREEN, COLOR_BORDER, (RECT_GAME_END_X[0], RECT_GAME_END_Y[0]),
                (RECT_GAME_END_X[1], RECT_GAME_END_Y[0]), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (RECT_GAME_END_X[0], RECT_GAME_END_Y[1]),
                (RECT_GAME_END_X[1], RECT_GAME_END_Y[1]), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (RECT_GAME_END_X[1], RECT_GAME_END_Y[0]),
                (RECT_GAME_END_X[1], RECT_GAME_END_Y[1]), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (RECT_GAME_END_X[0], RECT_GAME_END_Y[0]),
                (RECT_GAME_END_X[0], RECT_GAME_END_Y[1]), width=2)


def draw_promotion_choice(selected_tile, white_move=True):
    pieces_str_white = ["wQ", "wN", "wR", "wB"]
    pieces_str_black = ["bQ", "bN", "bR", "bB"]
    pieces_str = pieces_str_white if white_move else pieces_str_black

    top_tile = tuple(selected_tile) if white_move else (4, selected_tile[1])
    top_left_coords = (top_tile[1] * SQUARE_SIZE, top_tile[0] * SQUARE_SIZE)
    top_right_coords = (top_tile[1] * SQUARE_SIZE + SQUARE_SIZE, top_tile[0] * SQUARE_SIZE)
    bottom_left_coords = (top_tile[1] * SQUARE_SIZE, top_tile[0] * SQUARE_SIZE + 4 * SQUARE_SIZE)
    bottom_right_coords = (top_tile[1] * SQUARE_SIZE + SQUARE_SIZE, top_tile[0] * SQUARE_SIZE + 4 * SQUARE_SIZE)

    p.draw.rect(SCREEN, COLOR_HIGHLIGHT,
                p.Rect(top_left_coords[0], top_left_coords[1], SQUARE_SIZE, 4 * SQUARE_SIZE))
    p.draw.line(SCREEN, COLOR_BORDER, top_left_coords, bottom_left_coords, width=2)
    p.draw.line(SCREEN, COLOR_BORDER, top_right_coords, bottom_right_coords, width=2)

    p.draw.line(SCREEN, COLOR_BORDER, top_left_coords, top_right_coords, width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (top_left_coords[0], top_left_coords[1] + SQUARE_SIZE),
                (top_right_coords[0], top_right_coords[1] + SQUARE_SIZE), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (top_left_coords[0], top_left_coords[1] + 2 * SQUARE_SIZE),
                (top_right_coords[0], top_right_coords[1] + 2 * SQUARE_SIZE), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, (top_left_coords[0], top_left_coords[1] + 3 * SQUARE_SIZE),
                (top_right_coords[0], top_right_coords[1] + 3 * SQUARE_SIZE), width=2)
    p.draw.line(SCREEN, COLOR_BORDER, bottom_left_coords, bottom_right_coords, width=2)

    for i, piece_str in enumerate(pieces_str):
        SCREEN.blit(PIECES[piece_str], p.Rect(top_left_coords[0], top_left_coords[1] + i * SQUARE_SIZE,
                                              SQUARE_SIZE, SQUARE_SIZE))


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
