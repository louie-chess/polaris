import zobrist
import chess
import numpy as np
import sqlite3
from tqdm import tqdm

DEFAULT_SIZE = 10007

class EvaluationsHashTable:
    def __init__(self, size=DEFAULT_SIZE, cur: sqlite3.Cursor=None):
        self.hash = np.uint64(0)
        self.table = [None] * size
        self.size = np.uint32(size)
        self.length = np.uint32()
        if cur is not None:
            self.load_db(cur)

    def hash_pieces(self, board: chess.Board):
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None: continue

            color = 1 if piece.color == chess.WHITE else 0
            piece_type = piece.piece_type - 1
            index = piece_type * 2 * 64 + color * 64 + square

            self.hash ^= zobrist.hashes[zobrist.PIECE_HASHES + index]

    def hash_turn(self, board: chess.Board):
        turn = 1 if board.turn == chess.WHITE else 0
        self.hash ^= np.uint64(zobrist.hashes[zobrist.TURN_HASHES + turn])

    def hash_castling_rights(self, board: chess.Board):
        for castling_right in range(len(zobrist.CASTLING_RIGHTS)):
            if board.castling_rights & castling_right > 0:
                self.hash ^= zobrist.hashes[zobrist.CASTLING_HASHES + castling_right]

    def hash_ep_square(self, board: chess.Board):
        if board.ep_square is None:
            return np.uint64(0)

        self.hash ^= np.uint64(zobrist.hashes[zobrist.EP_HASHES + board.ep_square])

    def reset_hash(self):
        self.hash = np.uint64(0)

    def hash_board(self, board: chess.Board):
        self.reset_hash()
        self.hash_pieces(board)
        self.hash_turn(board)
        self.hash_castling_rights(board)
        self.hash_ep_square(board)

    def load_db(self, cur: sqlite3.Cursor):
        cur.execute("SELECT zobrist, binary, score FROM evaluations")
        evaluations = cur.fetchall()
        self.length = len(evaluations)

        for zobrist, binary, score in tqdm(evaluations, "Loading database"):
            zobrist = np.frombuffer(zobrist, dtype=np.uint64)[0]
            index = zobrist % self.size

            self.table[index] = (binary, score)

    def __setitem__(self, board, node):
        self.hash_board(board)
        index = self.hash % self.size
        self.table[index] = node
        self.length += 1

    def __getitem__(self, board):
        self.hash_board(board)
        index = self.hash % self.size

        return self.table[index]
    
    def __len__(self):
        return self.length