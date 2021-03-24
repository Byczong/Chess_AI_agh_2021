# Engine file - current chessboard state and valid moves

class ChessboardState:
    def __init__(self):
        self.board = None   # TODO: Determine the way to store info (piece/square - oriented)
        self.white_to_move = True
        self.moveLog = []
