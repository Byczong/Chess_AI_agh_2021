import Chess_AI.Engine.Chessboard as chessboard

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
        self.position_tables[chessboard.PieceType.KING] = self.king_table
        self.position_tables[chessboard.PieceType.QUEEN] = self.queen_table
        self.position_tables[chessboard.PieceType.ROOK] = self.rook_table
        self.position_tables[chessboard.PieceType.BISHOP] = self.bishop_table
        self.position_tables[chessboard.PieceType.KNIGHT] = self.knight_table
        self.position_tables[chessboard.PieceType.PAWN] = self.pawn_table

        self.values = {chessboard.PieceType.KING: 0, chessboard.PieceType.QUEEN: 900, chessboard.PieceType.ROOK: 500,
                       chessboard.PieceType.BISHOP: 330, chessboard.PieceType.KNIGHT: 320,
                       chessboard.PieceType.PAWN: 100}

    def evaluate(self):
        """Get board evaluation score"""
        game_state = self.board_state.game_state()
        if game_state == chessboard.GameState.CHECKMATE:
            return -99999 if self.board_state.white_to_move else 99999
        elif game_state == chessboard.GameState.STALEMATE or game_state == chessboard.GameState.INSUFFICIENT_MATERIAL:
            return 0
        else:
            pieces_lists = self.board_state.get_pieces_lists()
            evaluation = self.material_score(pieces_lists) + self.position_score(pieces_lists)
            return evaluation if self.board_state.white_to_move else -evaluation

    def material_score(self, pieces_lists):
        """Get board material evaluation score"""
        material_score = 0
        for piece_type in chessboard.PieceType.piece_type_list():
            material_score += self.values[piece_type] * (len(pieces_lists[piece_type][chessboard.Color.WHITE]) -
                                                         len(pieces_lists[piece_type][chessboard.Color.BLACK]))
        return material_score

    def position_score(self, pieces_lists):
        """Get board position evaluation score"""
        position_score = 0
        for piece_type in chessboard.PieceType.piece_type_list():
            for piece in pieces_lists[piece_type][chessboard.Color.WHITE]:
                position_score += self.position_tables[piece_type][piece.position[0]][piece.position[1]]
            for piece in pieces_lists[piece_type][chessboard.Color.BLACK]:
                position_score -= self.position_tables[piece_type][7 - piece.position[0]][piece.position[1]]
        return position_score


class ChessAI:
    def __init__(self, board_state):
        self.board_state = board_state
        self.evaluator = BoardEvaluation(board_state)

    def ai_move(self, depth=3):
        """Get next AI move. Move searching depth is set by depth"""
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