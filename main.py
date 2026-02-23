import chess.pgn
import chess.engine
import hashtable
import utils
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

def insert_evaluation(board: chess.Board, engine: chess.engine.SimpleEngine, conn: sqlite3.Connection) -> int:
    binary = utils.binary(board)
    info = engine.analyse(board, chess.engine.Limit(depth=10))
    score = info["score"].relative.score(mate_score=100000)

    conn.execute('INSERT INTO evaluations (binary, score) VALUES (?, ?)', (binary, score))
    conn.commit()

    return binary, score

def insert_pgn(pgn, boards: hashtable.HashTable, engine: chess.engine.SimpleEngine, conn: sqlite3.Connection):
    while len(boards) < boards.size:
        game = chess.pgn.read_game(pgn)
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
            if boards[board] is not None: continue

            _, score = insert_evaluation(board, engine, conn)
            boards[board] = board

            print(f"finished board {len(boards)}/{boards.size} with score {score}.")

def main():
    pgn = open(os.getenv("GAMES_PATH"))
    boards = hashtable.HashTable(int(os.getenv("BOARDS_SIZE")))
    engine = chess.engine.SimpleEngine.popen_uci(os.getenv("STOCKFISH_PATH"))
    conn = sqlite3.connect("evaluations.db")

    conn.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            binary BLOB NOT NULL,
            score INT NOT NULL
        )
    ''')

    conn.commit()

    insert_pgn(pgn, boards, engine, conn)
    conn.close()
    engine.quit()

if __name__ == "__main__":
    main()