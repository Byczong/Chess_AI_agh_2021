class GameState:
    CHECKMATE, STALEMATE, CHECK, CONTINUE, INSUFFICIENT_MATERIAL = range(5)


class Color:
    WHITE, BLACK = range(2)


class PieceType:
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN = range(6)


class ChessboardState:
    # TODO: UNDO MOVES
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self.init_board()
        self.white_to_move = True
        self.white_king = self.board[7][4]
        self.black_king = self.board[0][4]
        self.move_counter = 0
        self.moves_history = []

    def init_board(self):
        for row in (0, 7):
            if row == 0:
                color = Color.BLACK
                pawns_row = row + 1
            else:
                color = Color.WHITE
                pawns_row = row - 1
            self.board[row][0] = Rook([row, 0], color, self)
            self.board[row][1] = Knight([row, 1], color, self)
            self.board[row][2] = Bishop([row, 2], color, self)
            self.board[row][3] = Queen([row, 3], color, self)
            self.board[row][4] = King([row, 4], color, self)
            self.board[row][5] = Bishop([row, 5], color, self)
            self.board[row][6] = Knight([row, 6], color, self)
            self.board[row][7] = Rook([row, 7], color, self)
            for pawns_column in range(8):
                self.board[pawns_row][pawns_column] = Pawn([pawns_row, pawns_column], color, self)

    def get_list_of_pieces(self, piece_type, color):
        pieces = []
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if piece is not None:
                    if piece.color == color and piece.type == piece_type:
                        pieces.append(piece)
        return pieces

    def get_current_color(self):
        if self.white_to_move:
            return Color.WHITE
        else:
            return Color.BLACK

    def legal_moves_generator(self):
        color = self.get_current_color()

        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if piece is not None:
                    if piece.color == color:
                        moves_list = piece.get_legal_moves_list()
                        if moves_list is not None:
                            for new_position in moves_list:
                                move = (piece.position, new_position)
                                yield move

    def is_capture(self, move):
        if self.board[move[1][0]][move[1][1]] is not None:
            return True
        if self.board[move[0][0]][move[0][1]].type == PieceType.PAWN and self.board[move[1][0]][move[1][1]] is None and\
                abs(move[1][1] - move[0][1]) == 1:
            return True
        return False

    def game_state(self):
        if self.is_insufficient_material():
            return GameState.INSUFFICIENT_MATERIAL

        is_any_move_possible = self.is_any_move_possible()
        if not is_any_move_possible:
            if self.is_check():
                return GameState.CHECKMATE
            else:
                return GameState.STALEMATE
        elif self.is_check():
            return GameState.CHECK
        else:
            return GameState.CONTINUE

    def is_any_move_possible(self):
        color = self.get_current_color()

        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if piece is not None:
                    if piece.color == color:
                        if piece.get_legal_moves_list() is not None:
                            return True
        return False

    def is_insufficient_material(self):
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if piece is not None:
                    if piece.type != PieceType.KING:
                        return False
        return True

    def is_check(self):
        if self.white_to_move:
            if self.is_move_valid(self.white_king.position, self.white_king.position):
                return False
            else:
                return True
        else:
            if self.is_move_valid(self.black_king.position, self.black_king.position):
                return False
            else:
                return True

    def is_move_valid(self, old_position, new_position):
        old_position_piece = self.board[old_position[0]][old_position[1]]
        new_position_piece = self.board[new_position[0]][new_position[1]]

        self.board[new_position[0]][new_position[1]] = old_position_piece
        self.board[old_position[0]][old_position[1]] = None
        old_position_piece.position = new_position

        if self.white_to_move:
            king = self.white_king
            pawn_row_step = -1
        else:
            king = self.black_king
            pawn_row_step = 1

        en_passant = False
        pawn = None
        if isinstance(old_position_piece, Pawn) and new_position_piece is None and \
                abs(new_position[1] - old_position[1]) == 1:
            pawn = self.board[new_position[0] - pawn_row_step][new_position[1]]
            self.board[new_position[0] - pawn_row_step][new_position[1]] = None
            en_passant = True

        for step in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            if not ChessboardState.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if isinstance(threat_position_piece, King):
                            self.board[old_position[0]][old_position[1]] = old_position_piece
                            self.board[new_position[0]][new_position[1]] = new_position_piece
                            old_position_piece.position = old_position
                            if en_passant:
                                self.board[pawn.position[0]][pawn.position[1]] = pawn
                            return False

        for step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            while not ChessboardState.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if isinstance(threat_position_piece, Rook) or isinstance(threat_position_piece, Queen):
                            self.board[old_position[0]][old_position[1]] = old_position_piece
                            self.board[new_position[0]][new_position[1]] = new_position_piece
                            old_position_piece.position = old_position
                            if en_passant:
                                self.board[pawn.position[0]][pawn.position[1]] = pawn
                            return False
                    break
                else:
                    threat_position[0] += step[0]
                    threat_position[1] += step[1]

        for step in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            while not ChessboardState.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if isinstance(threat_position_piece, Bishop) or isinstance(threat_position_piece, Queen):
                            self.board[old_position[0]][old_position[1]] = old_position_piece
                            self.board[new_position[0]][new_position[1]] = new_position_piece
                            old_position_piece.position = old_position
                            if en_passant:
                                self.board[pawn.position[0]][pawn.position[1]] = pawn
                            return False
                    break
                else:
                    threat_position[0] += step[0]
                    threat_position[1] += step[1]

        for step in ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            if not ChessboardState.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if isinstance(threat_position_piece, Knight):
                            self.board[old_position[0]][old_position[1]] = old_position_piece
                            self.board[new_position[0]][new_position[1]] = new_position_piece
                            old_position_piece.position = old_position
                            if en_passant:
                                self.board[pawn.position[0]][pawn.position[1]] = pawn
                            return False

        for step in ((pawn_row_step, -1), (pawn_row_step, 1)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            if not ChessboardState.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if isinstance(threat_position_piece, Pawn):
                            self.board[old_position[0]][old_position[1]] = old_position_piece
                            self.board[new_position[0]][new_position[1]] = new_position_piece
                            old_position_piece.position = old_position
                            if en_passant:
                                self.board[pawn.position[0]][pawn.position[1]] = pawn
                            return False

        self.board[old_position[0]][old_position[1]] = old_position_piece
        self.board[new_position[0]][new_position[1]] = new_position_piece
        old_position_piece.position = old_position
        if en_passant:
            self.board[pawn.position[0]][pawn.position[1]] = pawn
        return True

    @staticmethod
    def is_move_out_of_board(position):
        if 7 >= position[0] >= 0 and 7 >= position[1] >= 0:
            return False
        else:
            return True


class Piece:
    def __init__(self, position, color, board_state):
        self.position = position
        self.color = color
        self.board_state = board_state

    def is_same_color(self, other_piece):
        if self.color == other_piece.color:
            return True
        else:
            return False

    def legal_moves(self):
        if (self.board_state.white_to_move and self.color == Color.WHITE) \
                or (not self.board_state.white_to_move and self.color == Color.BLACK):
            for move in self.pseudo_legal_moves():
                if self.board_state.is_move_valid(self.position, move):
                    yield move

    def get_legal_moves_list(self):
        legal_moves_list = []
        for move in self.legal_moves():
            new_move = move.copy()
            legal_moves_list.append(new_move)
        if len(legal_moves_list) == 0:
            return None
        return legal_moves_list

    def move(self, new_position):
        self.board_state.moves_history.append((self.position, new_position))
        self.board_state.move_counter += 1
        self.board_state.board[self.position[0]][self.position[1]] = None
        self.board_state.board[new_position[0]][new_position[1]] = self
        self.position = new_position
        if self.board_state.white_to_move:
            self.board_state.white_to_move = False
        else:
            self.board_state.white_to_move = True

    def pseudo_legal_moves(self):
        raise NotImplementedError("Method is not implemented")

    def __str__(self):
        raise NotImplementedError("Method is not implemented")


class King(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.first_move = True
        self.type = PieceType.KING

    def pseudo_legal_moves(self):
        for step in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            if not ChessboardState.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                else:
                    yield new_position

        if self.color == Color.WHITE:
            row = 7
        else:
            row = 0
        piece = self.board_state.board[row][7]
        if self.first_move and piece is not None:
            if isinstance(piece, Rook):
                if piece.first_move and self.board_state.board[row][5] is None and \
                        self.board_state.board[row][6] is None:
                    if self.board_state.is_move_valid([row, 4], [row, 5]) and \
                            self.board_state.is_move_valid([row, 7], [row, 5]):
                        yield [row, 6]

        piece = self.board_state.board[row][0]
        if self.first_move and piece is not None:
            if isinstance(piece, Rook):
                if piece.first_move and self.board_state.board[row][3] is None and \
                        self.board_state.board[row][2] is None and self.board_state.board[row][1] is None:
                    if self.board_state.is_move_valid([row, 4], [row, 3]) and \
                            self.board_state.is_move_valid([row, 0], [row, 3]):
                        yield [row, 2]

    def move(self, new_position):
        self.board_state.moves_history.append((self.position, new_position))
        self.board_state.move_counter += 1

        if abs(self.position[1] - new_position[1]) == 2:
            if new_position == (7, 6):
                rook = self.board_state.board[7][7]
                self.board_state.board[7][5] = rook
                self.board_state.board[7][7] = None
                rook.position = [7, 5]
                rook.first_move = False
            elif new_position == (7, 2):
                rook = self.board_state.board[7][0]
                self.board_state.board[7][3] = rook
                self.board_state.board[7][0] = None
                rook.position = [7, 3]
                rook.first_move = False
            elif new_position == (0, 6):
                rook = self.board_state.board[0][7]
                self.board_state.board[0][5] = rook
                self.board_state.board[0][7] = None
                rook.position = [0, 5]
                rook.first_move = False
            elif new_position == (0, 2):
                rook = self.board_state.board[0][0]
                self.board_state.board[0][3] = rook
                self.board_state.board[0][0] = None
                rook.position = [0, 3]
                rook.first_move = False

        self.board_state.board[self.position[0]][self.position[1]] = None
        self.board_state.board[new_position[0]][new_position[1]] = self
        self.position = new_position

        if self.first_move:
            self.first_move = False

        if self.board_state.white_to_move:
            self.board_state.white_to_move = False
        else:
            self.board_state.white_to_move = True

    def __str__(self):
        return "wK" if self.color == Color.WHITE else "bK"


class Queen(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.type = PieceType.QUEEN

    def pseudo_legal_moves(self):
        for step in ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            while not ChessboardState.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                    break
                else:
                    yield new_position
                    new_position[0] += step[0]
                    new_position[1] += step[1]

    def __str__(self):
        return "wQ" if self.color == Color.WHITE else "bQ"


class Rook(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.first_move = True
        self.type = PieceType.ROOK

    def pseudo_legal_moves(self):
        for step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            while not ChessboardState.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                    break
                else:
                    yield new_position
                    new_position[0] += step[0]
                    new_position[1] += step[1]

    def move(self, new_position):
        self.board_state.moves_history.append((self.position, new_position))
        self.board_state.move_counter += 1

        self.board_state.board[self.position[0]][self.position[1]] = None
        self.board_state.board[new_position[0]][new_position[1]] = self
        self.position = new_position

        if self.first_move:
            self.first_move = False

        if self.board_state.white_to_move:
            self.board_state.white_to_move = False
        else:
            self.board_state.white_to_move = True

    def __str__(self):
        return "wR" if self.color == Color.WHITE else "bR"


class Bishop(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.type = PieceType.BISHOP

    def pseudo_legal_moves(self):
        for step in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            while not ChessboardState.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                    break
                else:
                    yield new_position
                    new_position[0] += step[0]
                    new_position[1] += step[1]

    def __str__(self):
        return "wB" if self.color == Color.WHITE else "bB"


class Knight(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.type = PieceType.KNIGHT

    def pseudo_legal_moves(self):
        for step in ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            if not ChessboardState.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                else:
                    yield new_position

    def __str__(self):
        return "wN" if self.color == Color.WHITE else "bN"


class Pawn(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.first_move = True
        self.last_move_number = None
        self.moved_by_two = False
        self.type = PieceType.PAWN

    def pseudo_legal_moves(self):
        if self.color == Color.WHITE:
            row_step = -1
        else:
            row_step = 1

        new_position = [self.position[0] + row_step, self.position[1]]
        if not ChessboardState.is_move_out_of_board(new_position):
            new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
            if new_position_piece is None:
                yield new_position
                new_position[0] += row_step
                if not ChessboardState.is_move_out_of_board(new_position) and self.first_move:
                    new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                    if new_position_piece is None:
                        yield new_position

        for step in ((row_step, -1), (row_step, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            if not ChessboardState.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position

        for step in ((0, -1), (0, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            if not ChessboardState.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece) and isinstance(new_position_piece, Pawn):
                        if new_position_piece.last_move_number == self.board_state.move_counter and \
                                new_position_piece.moved_by_two:
                            new_position[0] += row_step
                            yield new_position

    def move(self, new_position):
        self.board_state.moves_history.append((self.position, new_position))
        self.board_state.move_counter += 1
        self.last_move_number = self.board_state.move_counter
        if abs(self.position[0] - new_position[0]) == 2:
            self.moved_by_two = True
        else:
            self.moved_by_two = False

        # en_passant
        if self.board_state.board[new_position[0]][new_position[1]] is None and \
                abs(new_position[1] - self.position[1]) == 1:
            if self.color == Color.WHITE:
                pawn_row_step = -1
            else:
                pawn_row_step = 1
            self.board_state.board[new_position[0] - pawn_row_step][new_position[1]] = None

        self.board_state.board[self.position[0]][self.position[1]] = None
        self.board_state.board[new_position[0]][new_position[1]] = self
        self.position = new_position

        # pawn promotion
        if self.color == Color.WHITE and new_position[0] == 0:
            promoted_pawn = Queen(new_position, self.color, self.board_state)
            self.board_state.board[new_position[0]][new_position[1]] = promoted_pawn
        elif self.color == Color.BLACK and new_position[0] == 7:
            promoted_pawn = Queen(new_position, self.color, self.board_state)
            self.board_state.board[new_position[0]][new_position[1]] = promoted_pawn

        if self.first_move:
            self.first_move = False

        if self.board_state.white_to_move:
            self.board_state.white_to_move = False
        else:
            self.board_state.white_to_move = True

    def __str__(self):
        return "wP" if self.color == Color.WHITE else "bP"


class BoardEvaluation:
    def __init__(self, board_state):
        self.board_state = board_state

        self.king_table = [[-30, -40, -40, -50, -50, -40, -40, -30],
                           [-30, -40, -40, -50, -50, -40, -40, -30],
                           [-30, -40, -40, -50, -50, -40, -40, -30],
                           [-30, -40, -40, -50, -50, -40, -40, -30],
                           [-20, -30, -30, -40, -40, -30, -30, -20],
                           [-10, -20, -20, -20, -20, -20, -20, -10],
                           [20, 20, 0, 0, 0, 0, 20, 20],
                           [20, 30, 10, 0, 0, 10, 30, 20]
                           ]
        self.queen_table = [[-20, -10, -10, -5, -5, -10, -10, -20],
                            [-10, 0, 0, 0, 0, 0, 0, -10],
                            [-10, 0, 5, 5, 5, 5, 0, -10],
                            [-5, 0, 5, 5, 5, 5, 0, -5],
                            [0, 0, 5, 5, 5, 5, 0, -5],
                            [-10, 5, 5, 5, 5, 5, 0, -10],
                            [-10, 0, 0, 0, 0, 0, 0, -10],
                            [-20, -10, -10, -5, -5, -10, -10, -20]
                            ]
        self.rook_table = [[0, 0, 0, 0, 0, 0, 0, 0],
                           [5, 10, 10, 10, 10, 10, 10, 5],
                           [-5, 0, 0, 0, 0, 0, 0, -5],
                           [-5, 0, 0, 0, 0, 0, 0, -5],
                           [-5, 0, 0, 0, 0, 0, 0, -5],
                           [-5, 0, 0, 0, 0, 0, 0, -5],
                           [-5, 0, 0, 0, 0, 0, 0, -5],
                           [0, 0, 0, 5, 5, 0, 0, 0]
                           ]
        self.bishop_table = [[-20, -10, -10, -10, -10, -10, -10, -20],
                             [-10, 0, 0, 0, 0, 0, 0, -10],
                             [-10, 0, 5, 10, 10, 5, 0, -10],
                             [-10, 5, 5, 10, 10, 5, 5, -10],
                             [-10, 0, 10, 10, 10, 10, 0, -10],
                             [-10, 10, 10, 10, 10, 10, 10, -10],
                             [-10, 5, 0, 0, 0, 0, 5, -10],
                             [-20, -10, -10, -10, -10, -10, -10, -20]
                             ]
        self.knight_table = [[-50, -40, -30, -30, -30, -30, -40, -50],
                             [-40, -20, 0, 0, 0, 0, -20, -40],
                             [-30, 0, 10, 15, 15, 10, 0, -30],
                             [-30, 5, 15, 20, 20, 15, 5, -30],
                             [-30, 0, 15, 20, 20, 15, 0, -30],
                             [-30, 5, 10, 15, 15, 10, 5, -30],
                             [-40, -20, 0, 5, 5, 0, -20, -40],
                             [-50, -40, -30, -30, -30, -30, -40, -50]
                             ]
        self.pawn_table = [[0, 0, 0, 0, 0, 0, 0, 0],
                           [50, 50, 50, 50, 50, 50, 50, 50],
                           [10, 10, 20, 30, 30, 20, 10, 10],
                           [5, 5, 10, 25, 25, 10, 5, 5],
                           [0, 0, 0, 20, 20, 0, 0, 0],
                           [5, -5, -10, 0, 0, -10, -5, 5],
                           [5, 10, 10, -20, -20, 10, 10, 5],
                           [0, 0, 0, 0, 0, 0, 0, 0]
                           ]

    def evaluate(self):
        game_state = self.board_state.game_state()
        if game_state == GameState.CHECKMATE:
            if self.board_state.white_to_move:
                return -9999
            else:
                return 9999
        elif game_state == GameState.STALEMATE or game_state == GameState.INSUFFICIENT_MATERIAL:
            return 0
        else:
            return self.evaluation_score()

    def evaluation_score(self):
        pieces_lists = [None] * 6
        for i in range(6):
            pieces_lists[i] = [[], []]
        for row in range(8):
            for column in range(8):
                piece = self.board_state.board[row][column]
                if piece is not None:
                    pieces_lists[piece.type][piece.color].append(piece)

        material_score = 100 * (len(pieces_lists[PieceType.PAWN][Color.WHITE]) - len(pieces_lists[PieceType.PAWN][Color.BLACK])) \
                         + 320 * (len(pieces_lists[PieceType.KNIGHT][Color.WHITE]) - len(pieces_lists[PieceType.KNIGHT][Color.BLACK])) \
                         + 330 * (len(pieces_lists[PieceType.BISHOP][Color.WHITE]) - len(pieces_lists[PieceType.BISHOP][Color.BLACK])) \
                         + 500 * (len(pieces_lists[PieceType.ROOK][Color.WHITE]) - len(pieces_lists[PieceType.ROOK][Color.BLACK])) \
                         + 900 * (len(pieces_lists[PieceType.QUEEN][Color.WHITE]) - len(pieces_lists[PieceType.QUEEN][Color.BLACK]))

        king_position_score = sum([self.king_table[piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.KING][Color.WHITE]])\
                              + sum([-self.king_table[7 - piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.KING][Color.BLACK]])

        queen_position_score = sum([self.queen_table[piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.QUEEN][Color.WHITE]])\
                              + sum([-self.queen_table[7 - piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.QUEEN][Color.BLACK]])

        rook_position_score = sum([self.rook_table[piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.ROOK][Color.WHITE]])\
                              + sum([-self.rook_table[7 - piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.ROOK][Color.BLACK]])

        bishop_position_score = sum([self.bishop_table[piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.BISHOP][Color.WHITE]])\
                              + sum([-self.bishop_table[7 - piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.KING][Color.BLACK]])

        knight_position_score = sum([self.knight_table[piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.KNIGHT][Color.WHITE]])\
                              + sum([-self.knight_table[7 - piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.KNIGHT][Color.BLACK]])

        pawn_position_score = sum([self.pawn_table[piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.PAWN][Color.WHITE]])\
                              + sum([-self.pawn_table[7 - piece.position[0]][piece.position[1]] for piece in pieces_lists[PieceType.PAWN][Color.BLACK]])

        evaluation = material_score + king_position_score + queen_position_score + rook_position_score \
                     + bishop_position_score + knight_position_score + pawn_position_score
        if self.board_state.white_to_move:
            return evaluation
        else:
            return -evaluation


class ChessAI:
    def __init__(self, board_state):
        self.board_state = board_state

    def ai_move(self, depth=3):
        board_state = self.board_state
        best_move = None
        best_value = -99999
        alpha = -100000
        beta = 100000
        for move in board_state.legal_moves_generator():

            board_state_after_move = ChessboardState()
            for history_move in board_state.moves_history:
                board_state_after_move.board[history_move[0][0]][history_move[0][1]].move(history_move[1])
            board_state_after_move.board[move[0][0]][move[0][1]].move(move[1])
            self.board_state = board_state_after_move

            board_value = -self.alphabeta(-beta, -alpha, depth - 1)
            if board_value > best_value:
                best_value = board_value
                best_move = move
            if board_value > alpha:
                alpha = board_value

            self.board_state = board_state

        return best_move

    def alphabeta(self, alpha, beta, depth):
        board_state = self.board_state
        best_score = -9999
        if depth == 0:
            return self.quiescence_search(alpha, beta)
        for move in board_state.legal_moves_generator():

            board_state_after_move = ChessboardState()
            for history_move in board_state.moves_history:
                board_state_after_move.board[history_move[0][0]][history_move[0][1]].move(history_move[1])
            board_state_after_move.board[move[0][0]][move[0][1]].move(move[1])
            self.board_state = board_state_after_move

            score = -self.alphabeta(-beta, -alpha, depth - 1)

            self.board_state = board_state
            if score >= beta:
                return score
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score
        return best_score

    def quiescence_search(self, alpha, beta):
        board_state = self.board_state
        evaluation = BoardEvaluation(board_state).evaluate()
        if evaluation >= beta:
            return beta
        if alpha < evaluation:
            alpha = evaluation

        for move in board_state.legal_moves_generator():
            if board_state.is_capture(move):

                board_state_after_move = ChessboardState()
                for history_move in board_state.moves_history:
                    board_state_after_move.board[history_move[0][0]][history_move[0][1]].move(history_move[1])
                board_state_after_move.board[move[0][0]][move[0][1]].move(move[1])
                self.board_state = board_state_after_move

                score = -self.quiescence_search(-beta, -alpha)

                self.board_state = board_state

                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score

        return alpha