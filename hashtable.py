import zobrist
import chess
import numpy as np

DEFAULT_SIZE = 10007

class HashTable:
    def __init__(self, size=DEFAULT_SIZE):
        self.table = [None] * size
        self.size = size
        self.length = 0
    
    def hash(self, board: chess.Board):
        hash = np.array(0, dtype=np.uint64)

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None: continue

            color = 1 if piece.color == chess.WHITE else 0
            piece_type = piece.piece_type - 1
            index = piece_type * 2 * 64 + color * 64 + square

            hash ^= zobrist.hashes[zobrist.PIECE_HASHES + index]

        hash ^= zobrist.hashes[zobrist.TURN_HASHES + (1 if board.turn == chess.WHITE else 0)]

        for castling_right in range(len(zobrist.CASTLING_RIGHTS)):
            if board.castling_rights & castling_right > 0:
                hash ^= zobrist.hashes[zobrist.CASTLING_HASHES + castling_right]

        if board.ep_square is not None:
            hash ^= zobrist.hashes[zobrist.EP_HASHES + board.ep_square]

        return hash
    
    def __setitem__(self, board, node):
        index = self.hash(board) % self.size
        self.table[index] = node
        self.length += 1

    def __getitem__(self, board):
        index = self.hash(board) % self.size

        return self.table[index]
    
    def __len__(self):
        return self.length