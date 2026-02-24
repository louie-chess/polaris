import chess.pgn
import chess.engine
import hashtable
import utils
import sqlite3
from dotenv import dotenv_values
import typing
from tqdm import tqdm

config = {
    **dotenv_values(".env"),
}

def insert_evaluation(board: chess.Board, boards: hashtable.EvaluationsHashTable, engine: chess.engine.SimpleEngine, conn: sqlite3.Connection, depth: int) -> int:
    binary = utils.binary(board)
    info = engine.analyse(board, chess.engine.Limit(depth=depth))
    score = info["score"].relative.score(mate_score=100000)
    boards[board] = { "binary": binary, "score": score, "engine": engine.id["name"], "depth": depth }
    zobrist = boards.hash.tobytes()

    conn.execute(
        "INSERT INTO evaluations (zobrist, binary, score, engine, depth) VALUES (?, ?, ?, ?, ?)",
        (zobrist, binary, score, engine.id["name"], depth))
    conn.commit()

    return zobrist, binary, score, engine.id["name"], depth

def insert_evaluations(game: chess.pgn.Game, boards: hashtable.EvaluationsHashTable, engine: chess.engine.SimpleEngine, conn: sqlite3.Connection, depth: int, fn: typing.Callable[[bytes, bytes, int, str, int], typing.Any]=None):
    board = game.board()

    for move in game.mainline_moves():
        board.push(move)
        board_entry = boards[board]
        if board_entry is not None and board_entry["depth"] >= depth: continue

        zobrist, binary, score, engine_name, depth = insert_evaluation(board, boards, engine, conn, depth)
        if fn is not None: fn(zobrist, binary, score, engine_name, depth)

def insert_pgn(pgn, boards: hashtable.EvaluationsHashTable, engine: chess.engine.SimpleEngine, conn: sqlite3.Connection, depth: int, pbar: tqdm=None):
    fn = lambda a,b,c,d,e: pbar.update()

    while len(boards) < boards.size:
        game = chess.pgn.read_game(pgn)
        if game is None: continue

        insert_evaluations(game, boards, engine, conn, depth, None if pbar is None else fn)

def main():
    pgn = open(config["GAMES_PATH"])
    engine = chess.engine.SimpleEngine.popen_uci(config["ENGINE_PATH"])
    conn = sqlite3.connect("evaluations.db")
    cur = conn.cursor()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            zobrist BLOB PRIMARY KEY,
            binary BLOB NOT NULL,
            score INT NOT NULL,
            engine TEXT,
            depth INT
        )
    """)

    conn.commit()

    boards = hashtable.EvaluationsHashTable(int(config["DB_SIZE"]), cur)
    pbar = tqdm(total=boards.size-len(boards))
    insert_pgn(pgn, boards, engine, conn, int(config["ENGINE_DEPTH"]), pbar)
    pgn.close()
    conn.close()
    engine.quit()

if __name__ == "__main__":
    main()