import chess
import numpy as np

def binary(board: chess.Board):
    return np.array([
        board.occupied_co[chess.WHITE] & board.pawns, # white pieces
        board.occupied_co[chess.WHITE] & board.knights,
        board.occupied_co[chess.WHITE] & board.bishops,
        board.occupied_co[chess.WHITE] & board.rooks,
        board.occupied_co[chess.WHITE] & board.queens,
        board.occupied_co[chess.WHITE] & board.kings,

        board.occupied_co[chess.BLACK] & board.pawns, # black pieces
        board.occupied_co[chess.BLACK] & board.knights,
        board.occupied_co[chess.BLACK] & board.bishops,
        board.occupied_co[chess.BLACK] & board.rooks,
        board.occupied_co[chess.BLACK] & board.queens,
        board.occupied_co[chess.BLACK] & board.kings,

        (1 if board.turn == chess.WHITE else 0), # side to move
        board.castling_rights, # castling rights
        (board.ep_square if board.ep_square else 0), # en passant
        board.halfmove_clock, # halfmove clock
        board.fullmove_number, # fullmove number
    ], dtype=np.uint64).tobytes()