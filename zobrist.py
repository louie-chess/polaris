import chess
import numpy as np

CASTLING_RIGHTS = [chess.BB_H1, chess.BB_A1, chess.BB_H8, chess.BB_A8]

pieces = len(chess.PIECE_TYPES) * len(chess.COLORS) * len(chess.SQUARES)
turn = len(chess.COLORS)
castling_rights = len(CASTLING_RIGHTS)
ep_square = len(chess.SQUARES)

rng = np.random.default_rng()

num_hashes = pieces + turn + castling_rights + ep_square
hashes = rng.integers(0, 2**64, size=num_hashes, dtype=np.uint64)

PIECE_HASHES = 0
TURN_HASHES = 768
CASTLING_HASHES = 770
EP_HASHES = 774