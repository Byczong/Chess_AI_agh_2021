class GameState:
    CHECKMATE, STALEMATE, CHECK, CONTINUE, INSUFFICIENT_MATERIAL = range(5)


class Color:
    WHITE, BLACK = range(2)


class PieceType:
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN = range(6)

    @staticmethod
    def piece_type_list():
        return [PieceType.KING, PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT, PieceType.PAWN]



class ChessboardState:
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

    def get_current_color(self):
        if self.white_to_move:
            return Color.WHITE
        else:
            return Color.BLACK

    def legal_moves(self):
        color = self.get_current_color()
        legal_moves_list = []
        for row in range(8):
            for column in range(8):
                piece = self.board[row][column]
                if piece is not None:
                    if piece.color == color:
                        moves_list = piece.get_legal_moves_list()
                        if moves_list is not None:
                            for new_position in moves_list:
                                move = [piece.position.copy(), new_position.copy()]
                                legal_moves_list.append(move)
        return legal_moves_list

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
        def undo(en_passant):
            self.board[old_position[0]][old_position[1]] = old_position_piece
            self.board[new_position[0]][new_position[1]] = new_position_piece
            old_position_piece.position = old_position
            if en_passant:
                self.board[pawn.position[0]][pawn.position[1]] = pawn

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
        if old_position_piece.type == PieceType.PAWN and new_position_piece is None and \
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
                        if threat_position_piece.type == PieceType.KING:
                            undo(en_passant)
                            return False

        for step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            while not ChessboardState.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if threat_position_piece.type == PieceType.ROOK or threat_position_piece.type == PieceType.QUEEN:
                            undo(en_passant)
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
                        if threat_position_piece.type == PieceType.BISHOP or threat_position_piece.type == PieceType.QUEEN:
                            undo(en_passant)
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
                        if threat_position_piece.type == PieceType.KNIGHT:
                            undo(en_passant)
                            return False

        for step in ((pawn_row_step, -1), (pawn_row_step, 1)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            if not ChessboardState.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if threat_position_piece.type == PieceType.PAWN:
                            undo(en_passant)
                            return False

        undo(en_passant)
        return True


    def undo_move(self):
        if len(self.moves_history) == 0:
            return
        self.move_counter -= 1
        move = self.moves_history.pop()

        start_position = move.start_position
        end_position = move.end_position
        moved_piece = move.moved_piece
        captured_piece = move.captured_piece

        moved_piece.position = start_position
        self.board[start_position[0]][start_position[1]] = moved_piece
        self.board[end_position[0]][end_position[1]] = None
        if captured_piece is not None:
            self.board[captured_piece.position[0]][captured_piece.position[1]] = captured_piece
            if captured_piece.color == moved_piece.color:
                if captured_piece.position == [7, 7]:
                    self.board[7][5] = None
                elif captured_piece.position == [7, 0]:
                    self.board[7][3] = None
                elif captured_piece.position == [0, 7]:
                    self.board[0][5] = None
                elif captured_piece.position == [0, 0]:
                    self.board[0][3] = None


        if moved_piece.type == PieceType.KING:
            if moved_piece.color == Color.WHITE:
                self.white_king = moved_piece
            else:
                self.black_king = moved_piece

        if self.white_to_move:
            self.white_to_move = False
        else:
            self.white_to_move = True

    @staticmethod
    def is_move_out_of_board(position):
        if 7 >= position[0] >= 0 and 7 >= position[1] >= 0:
            return False
        else:
            return True


class Move:
    def __init__(self, start_position, end_position, moved_piece, captured_piece):
        self.start_position = start_position
        self.end_position = end_position
        self.moved_piece = moved_piece
        self.captured_piece = captured_piece


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
        self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), self, self.board_state.board[new_position[0]][new_position[1]]))
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
            if piece.type == PieceType.ROOK:
                if piece.first_move and self.board_state.board[row][5] is None and \
                        self.board_state.board[row][6] is None:
                    if self.board_state.is_move_valid([row, 4], [row, 5]) and \
                            self.board_state.is_move_valid([row, 7], [row, 5]):
                        yield [row, 6]

        piece = self.board_state.board[row][0]
        if self.first_move and piece is not None:
            if piece.type == PieceType.ROOK:
                if piece.first_move and self.board_state.board[row][3] is None and \
                        self.board_state.board[row][2] is None and self.board_state.board[row][1] is None:
                    if self.board_state.is_move_valid([row, 4], [row, 3]) and \
                            self.board_state.is_move_valid([row, 0], [row, 3]):
                        yield [row, 2]

    def move(self, new_position):
        self.board_state.move_counter += 1
        castling = False
        if abs(self.position[1] - new_position[1]) == 2:
            castling = True
            if new_position == [7, 6]:
                rook = self.board_state.board[7][7]

                king = King(self.position.copy(), self.color, self.board_state)
                if not self.first_move:
                    king.first_move = False
                rook_copy = Rook(rook.position.copy(), self.color, self.board_state)
                if not rook.first_move:
                    rook_copy.first_move = False
                self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), king, rook_copy))

                self.board_state.board[7][5] = rook
                self.board_state.board[7][7] = None
                rook.position = [7, 5]
                rook.first_move = False
            elif new_position == [7, 2]:
                rook = self.board_state.board[7][0]

                king = King(self.position.copy(), self.color, self.board_state)
                if not self.first_move:
                    king.first_move = False
                rook_copy = Rook(rook.position.copy(), self.color, self.board_state)
                if not rook.first_move:
                    rook_copy.first_move = False
                self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), king, rook_copy))

                self.board_state.board[7][3] = rook
                self.board_state.board[7][0] = None
                rook.position = [7, 3]
                rook.first_move = False
            elif new_position == [0, 6]:
                rook = self.board_state.board[0][7]

                king = King(self.position.copy(), self.color, self.board_state)
                if not self.first_move:
                    king.first_move = False
                rook_copy = Rook(rook.position.copy(), self.color, self.board_state)
                if not rook.first_move:
                    rook_copy.first_move = False
                self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), king, rook_copy))

                self.board_state.board[0][5] = rook
                self.board_state.board[0][7] = None
                rook.position = [0, 5]
                rook.first_move = False
            elif new_position == [0, 2]:
                rook = self.board_state.board[0][0]

                king = King(self.position.copy(), self.color, self.board_state)
                if not self.first_move:
                    king.first_move = False
                rook_copy = Rook(rook.position.copy(), self.color, self.board_state)
                if not rook.first_move:
                    rook_copy.first_move = False
                self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), king, rook_copy))

                self.board_state.board[0][3] = rook
                self.board_state.board[0][0] = None
                rook.position = [0, 3]
                rook.first_move = False

        king = King(self.position.copy(), self.color, self.board_state)
        if not self.first_move:
            king.first_move = False
        if not castling:
            self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), king, self.board_state.board[new_position[0]][new_position[1]]))

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
        rook = Rook(self.position.copy(), self.color, self.board_state)
        if not self.first_move:
            rook.first_move = False
        self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), rook,
                                                   self.board_state.board[new_position[0]][new_position[1]]))
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
                    if not self.is_same_color(new_position_piece) and new_position_piece.type == PieceType.PAWN:
                        if new_position_piece.last_move_number == self.board_state.move_counter and \
                                new_position_piece.moved_by_two:
                            new_position[0] += row_step
                            yield new_position

    def move(self, new_position):
        pawn = Pawn(self.position.copy(), self.color, self.board_state)
        if not self.first_move:
            pawn.first_move = False
        if self.moved_by_two:
            pawn.moved_by_two = True
        pawn.last_move_number = self.last_move_number

        self.board_state.move_counter += 1
        self.last_move_number = self.board_state.move_counter
        if abs(self.position[0] - new_position[0]) == 2:
            self.moved_by_two = True
        else:
            self.moved_by_two = False

        en_passant = False
        # en_passant
        if self.board_state.board[new_position[0]][new_position[1]] is None and \
                abs(new_position[1] - self.position[1]) == 1:
            en_passant = True
            if self.color == Color.WHITE:
                pawn_row_step = -1
            else:
                pawn_row_step = 1
            self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), pawn,
                                                       self.board_state.board[new_position[0] - pawn_row_step][new_position[1]]))
            self.board_state.board[new_position[0] - pawn_row_step][new_position[1]] = None


        pawn_promotion = False
        # pawn promotion
        if self.color == Color.WHITE and new_position[0] == 0:
            pawn_promotion = True
            self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), pawn,
                                                       self.board_state.board[new_position[0]][new_position[1]]))
            promoted_pawn = Queen(new_position, self.color, self.board_state)
            self.board_state.board[new_position[0]][new_position[1]] = promoted_pawn
        elif self.color == Color.BLACK and new_position[0] == 7:
            pawn_promotion = True
            self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), pawn,
                                                       self.board_state.board[new_position[0]][new_position[1]]))
            promoted_pawn = Queen(new_position, self.color, self.board_state)
            self.board_state.board[new_position[0]][new_position[1]] = promoted_pawn

        if not en_passant and not pawn_promotion:
            self.board_state.moves_history.append(Move(self.position.copy(), new_position.copy(), pawn,
                                                       self.board_state.board[new_position[0]][new_position[1]]))

        self.board_state.board[self.position[0]][self.position[1]] = None
        if not pawn_promotion:
            self.board_state.board[new_position[0]][new_position[1]] = self
        self.position = new_position

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
        self.position_tables = [None] * 6
        self.position_tables[PieceType.KING] = self.king_table
        self.position_tables[PieceType.QUEEN] = self.queen_table
        self.position_tables[PieceType.ROOK] = self.rook_table
        self.position_tables[PieceType.BISHOP] = self.bishop_table
        self.position_tables[PieceType.KNIGHT] = self.knight_table
        self.position_tables[PieceType.PAWN] = self.pawn_table

    def evaluate(self):
        game_state = self.board_state.game_state()
        if game_state == GameState.CHECKMATE:
            if self.board_state.white_to_move:
                return -99999
            else:
                return 99999
        elif game_state == GameState.STALEMATE or game_state == GameState.INSUFFICIENT_MATERIAL:
            return 0
        else:
            pieces_lists = [None] * 6
            for i in range(6):
                pieces_lists[i] = [[], []]
            for row in range(8):
                for column in range(8):
                    piece = self.board_state.board[row][column]
                    if piece is not None:
                        pieces_lists[piece.type][piece.color].append(piece)
            evaluation = self.material_score(pieces_lists) + self.position_score(pieces_lists)
            if self.board_state.white_to_move:
                return evaluation
            else:
                return -evaluation

    @staticmethod
    def material_score(pieces_lists):
        material_score = 0
        for piece_type in PieceType.piece_type_list():
            if piece_type == PieceType.KING:
                continue
            value = None
            if piece_type == PieceType.QUEEN:
                value = 900
            elif piece_type == PieceType.ROOK:
                value = 500
            elif piece_type == PieceType.BISHOP:
                value = 330
            elif piece_type == PieceType.KNIGHT:
                value = 320
            elif piece_type == PieceType.PAWN:
                value = 100
            material_score += value * (len(pieces_lists[piece_type][Color.WHITE]) - len(pieces_lists[piece_type][Color.BLACK]))
        return material_score

    def position_score(self, pieces_lists):
        position_score = 0
        for piece_type in PieceType.piece_type_list():
            for piece in pieces_lists[piece_type][Color.WHITE]:
                position_score += self.position_tables[piece_type][piece.position[0]][piece.position[1]]
            for piece in pieces_lists[piece_type][Color.BLACK]:
                position_score -= self.position_tables[piece_type][7 - piece.position[0]][piece.position[1]]
        return position_score




class ChessAI:
    def __init__(self, board_state):
        self.board_state = board_state
        self.evaluator = BoardEvaluation(board_state)

    def ai_move(self, depth=3):
        best_move = None
        best_board_evaluation = -99999
        alpha = -100000
        beta = 100000
        for move in self.board_state.legal_moves():
            self.board_state.board[move[0][0]][move[0][1]].move(move[1])
            board_evaluation = -self.alphabeta(-beta, -alpha, depth - 1)
            if board_evaluation > best_board_evaluation:
                best_board_evaluation = board_evaluation
                best_move = move
            if board_evaluation > alpha:
                alpha = board_evaluation
            self.board_state.undo_move()
        return best_move

    def alphabeta(self, alpha, beta, depth):
        best_board_evaluation = -99999
        if depth == 0:
            return self.quiescence_search(alpha, beta)
        for move in self.board_state.legal_moves():
            self.board_state.board[move[0][0]][move[0][1]].move(move[1])
            board_evaluation = -self.alphabeta(-beta, -alpha, depth - 1)
            self.board_state.undo_move()
            if board_evaluation >= beta:
                return board_evaluation
            if board_evaluation > best_board_evaluation:
                best_board_evaluation = board_evaluation
            if board_evaluation > alpha:
                alpha = board_evaluation
        return best_board_evaluation

    def quiescence_search(self, alpha, beta):
        evaluation = self.evaluator.evaluate()
        if evaluation >= beta:
            return beta
        if alpha < evaluation:
            alpha = evaluation
        for move in self.board_state.legal_moves():
            if self.board_state.is_capture(move):
                self.board_state.board[move[0][0]][move[0][1]].move(move[1])
                score = -self.quiescence_search(-beta, -alpha)
                self.board_state.undo_move()
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha
