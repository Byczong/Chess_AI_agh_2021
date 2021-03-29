# Engine file - current chessboard state and valid moves

class ChessboardState:
    def __init__(self):
        self.board = None   # TODO: Determine the way to store info (piece/square - oriented)
        self.white_to_move = True
        self.moveLog = []


class Piece:
    def __init__(self, position, color):
        self.position = position
        self.color = color


class King(Piece):
    def __init__(self, position, image):
        super().__init__(position)
        self.image = image

    def possible_moves(self):
        pass

    def move(self, new_position):
        self.position = new_position


class Bishop(Piece):
    def __init__(self, position, image):
        super().__init__(position)
        self.image = image

    def possible_moves(self):
        pass

    def move(self, new_position):
        self.position = new_position


class Rook(Piece):
    def __init__(self, position, image):
        super().__init__(position)
        self.image = image

    def possible_moves(self):
        pass

    def move(self, new_position):
        self.position = new_position


class Knight(Piece):
    def __init__(self, position, image):
        super().__init__(position)
        self.image = image

    def possible_moves(self):
        pass

    def move(self, new_position):
        self.position = new_position


class Pawn(Piece):
    def __init__(self, position, image):
        super().__init__(position)
        self.image = image

    def possible_moves(self):
        pass

    def move(self, new_position):
        self.position = new_position