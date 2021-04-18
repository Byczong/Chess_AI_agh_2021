# Engine file - current chessboard state and valid moves

class ChessboardState:
    def __init__(self):
        self.board = [[None] * 8 for i in range(8)]
        self.init_board()
        self.white_to_move = True
        self.white_king = self.board[7][4]
        self.black_king = self.board[0][4]
        self.moveLog = []
        for move in self.board[7][4].legal_moves():
            print(move)

    def init_board(self):
        for row in (0, 7):
            if row == 0:
                color = "black"
                pawns_row = row + 1
            else:
                color = "white"
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

        for step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            while not self.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if isinstance(threat_position_piece, Rook) or isinstance(threat_position_piece, Queen) \
                                or isinstance(threat_position_piece, King):
                            self.board[old_position[0]][old_position[1]] = old_position_piece
                            self.board[new_position[0]][new_position[1]] = new_position_piece
                            old_position_piece.position = old_position
                            return False
                    break
                else:
                    threat_position[0] += step[0]
                    threat_position[1] += step[1]

        for step in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            while not self.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if isinstance(threat_position_piece, Bishop) or isinstance(threat_position_piece, Queen) \
                                or isinstance(threat_position_piece, King):
                            self.board[old_position[0]][old_position[1]] = old_position_piece
                            self.board[new_position[0]][new_position[1]] = new_position_piece
                            old_position_piece.position = old_position
                            return False
                    break
                else:
                    threat_position[0] += step[0]
                    threat_position[1] += step[1]

        for step in ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            if not self.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if isinstance(threat_position_piece, Knight):
                            self.board[old_position[0]][old_position[1]] = old_position_piece
                            self.board[new_position[0]][new_position[1]] = new_position_piece
                            old_position_piece.position = old_position
                            return False

        for step in ((pawn_row_step, -1), (pawn_row_step, 1)):
            threat_position = [king.position[0] + step[0], king.position[1] + step[1]]
            if not self.is_move_out_of_board(threat_position):
                threat_position_piece = self.board[threat_position[0]][threat_position[1]]
                if threat_position_piece is not None:
                    if not king.is_same_color(threat_position_piece):
                        if isinstance(threat_position_piece, Pawn):
                            self.board[old_position[0]][old_position[1]] = old_position_piece
                            self.board[new_position[0]][new_position[1]] = new_position_piece
                            old_position_piece.position = old_position
                            return False

        self.board[old_position[0]][old_position[1]] = old_position_piece
        self.board[new_position[0]][new_position[1]] = new_position_piece
        old_position_piece.position = old_position
        return True

    def move(self, old_position, new_position):
        piece = self.board[old_position[0]][old_position[1]]
        self.board[new_position[0]][new_position[1]] = piece
        self.board[old_position[0]][old_position[1]] = None
        piece.position = new_position
        if self.white_to_move:
            self.white_to_move = False
        else:
            self.white_to_move = True

    def is_move_out_of_board(self, position):
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
        for move in self.pseudo_legal_moves():
            if self.board_state.is_move_valid(self.position, move):
                yield move

    def pseudo_legal_moves(self):
        raise NotImplementedError("Method is not implemented")


class King(Piece):
    def pseudo_legal_moves(self):
        for step in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            if not self.board_state.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                else:
                    yield new_position


class Queen(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.value = 9

    def pseudo_legal_moves(self):
        for step in ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            while not self.board_state.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                    break
                else:
                    yield new_position
                    new_position[0] += step[0]
                    new_position[1] += step[1]


class Rook(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.value = 5

    def pseudo_legal_moves(self):
        for step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            while not self.board_state.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                    break
                else:
                    yield new_position
                    new_position[0] += step[0]
                    new_position[1] += step[1]


class Bishop(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.value = 3

    def pseudo_legal_moves(self):
        for step in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            while not self.board_state.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                    break
                else:
                    yield new_position
                    new_position[0] += step[0]
                    new_position[1] += step[1]


class Knight(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.value = 3

    def pseudo_legal_moves(self):
        for step in ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            if not self.board_state.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
                else:
                    yield new_position


class Pawn(Piece):
    def __init__(self, position, color, board_state):
        super().__init__(position, color, board_state)
        self.value = 1
        self.first_move = True

    def pseudo_legal_moves(self):
        if self.color == "white":
            row_step = -1
        else:
            row_step = 1

        new_position = [self.position[0] + row_step, self.position[1]]
        if not self.board_state.is_move_out_of_board(new_position):
            new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
            if new_position_piece is None:
                yield new_position

                new_position[0] += row_step
                if not self.board_state.is_move_out_of_board(new_position) and self.first_move:
                    new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                    if new_position_piece is None:
                        yield new_position

        for step in ((row_step, -1), (row_step, 1)):
            new_position = [self.position[0] + step[0], self.position[1] + step[1]]
            if not self.board_state.is_move_out_of_board(new_position):
                new_position_piece = self.board_state.board[new_position[0]][new_position[1]]
                if new_position_piece is not None:
                    if not self.is_same_color(new_position_piece):
                        yield new_position
