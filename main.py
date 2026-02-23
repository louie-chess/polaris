import chess.pgn
import chess.engine
import hashtable
import utils
import sqlite3
from dotenv import load_dotenv
import os
import typing
from tqdm import tqdm

load_dotenv()

def insert_evaluation(board: chess.Board, boards: hashtable.EvaluationsHashTable, engine: chess.engine.SimpleEngine, conn: sqlite3.Connection) -> int:
    binary = utils.binary(board)
    depth = os.getenv("ENGINE_DEPTH", 12)
    info = engine.analyse(board, chess.engine.Limit(depth))
    score = info["score"].relative.score(mate_score=100000)
    boards[board] = (binary, score)
    zobrist = boards.hash.tobytes()

    conn.execute(
        "INSERT INTO evaluations (zobrist, binary, score) VALUES (?, ?, ?)",
        (zobrist, binary, score))
    conn.commit()

    return binary, score

def insert_evaluations(game: chess.pgn.Game, boards: hashtable.EvaluationsHashTable, engine: chess.engine.SimpleEngine, conn: sqlite3.Connection, fn: typing.Callable[[bytes, int], typing.Any]=None):
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
        if boards[board] is not None: continue

        binary, score = insert_evaluation(board, boards, engine, conn)
        if fn is not None: fn(binary, score)

def insert_pgn(pgn, boards: hashtable.EvaluationsHashTable, engine: chess.engine.SimpleEngine, conn: sqlite3.Connection, pbar: tqdm=None):
    while len(boards) < boards.size:
        game = chess.pgn.read_game(pgn)
        if game is None: continue

        fn = lambda x,y: pbar.update()
        insert_evaluations(game, boards, engine, conn, None if pbar is None else fn)

def main():
    games_path, engine_path = os.getenv("GAMES_PATH"), os.getenv("ENGINE_PATH")
    if games_path is None or engine_path is None:
        raise KeyError("could not find environment variables")

    pgn = open(games_path)
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    conn = sqlite3.connect("evaluations.db")
    cur = conn.cursor()
    boards = hashtable.EvaluationsHashTable(int(os.getenv("BOARDS_SIZE", 10007)), cur)
    pbar = tqdm(total=boards.size-len(boards), desc="Loading games")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            zobrist BLOB PRIMARY KEY,
            binary BLOB NOT NULL,
            score INT NOT NULL
        )
    """)

    conn.commit()

    insert_pgn(pgn, boards, engine, conn, pbar)
    conn.close()
    engine.quit()

if __name__ == "__main__":
    main()