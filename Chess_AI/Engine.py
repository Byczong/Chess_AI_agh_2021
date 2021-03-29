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

    def move(self, new_position):
        self.position = new_position


class King(Piece):
    def __init__(self, position, color, image):
        super().__init__(position, color)
        self.image = image

    def possible_moves(self):
        pass


class Bishop(Piece):
    def __init__(self, position, color, image):
        super().__init__(position, color)
        self.image = image

    def possible_moves(self):
        pass


class Rook(Piece):
    def __init__(self, position, color, image):
        super().__init__(position, color)
        self.image = image

    def possible_moves(self):
        pass


class Knight(Piece):
    def __init__(self, position, color, image):
        super().__init__(position, color)
        self.image = image

    def possible_moves(self):
        pass


class Pawn(Piece):
    def __init__(self, position, color, image):
        super().__init__(position, color)
        self.image = image

    def possible_moves(self):
        pass