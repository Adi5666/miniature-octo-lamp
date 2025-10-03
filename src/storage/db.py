import sqlite3
import threading
from pathlib import Path
import time

DB_PATH = Path(__file__).resolve().parent.parent.parent / "omniverse.db"
_lock = threading.Lock()

def init():
    with _lock, sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            shards INTEGER DEFAULT 0,
            captures INTEGER DEFAULT 0,
            badges TEXT DEFAULT ''
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            guild_id INTEGER,
            name TEXT,
            series TEXT,
            rarity TEXT,
            ts INTEGER
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS incense (
            guild_id INTEGER,
            channel_id INTEGER,
            expires_ts INTEGER,
            PRIMARY KEY (guild_id, channel_id)
        )""")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_captures_guild_ts ON captures(guild_id, ts);")
        con.commit()

def exec(query, params=()):
    with _lock, sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(query, params)
        con.commit()
        return cur

def fetchall(query, params=()):
    with _lock, sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(query, params)
        return cur.fetchall()

def get_user(user_id: int):
    row = exec("SELECT shards, captures, badges FROM users WHERE user_id=?", (user_id,)).fetchone()
    if row is None:
        exec("INSERT INTO users (user_id, shards, captures, badges) VALUES (?, 0, 0, '')", (user_id,))
        return 0, 0, ''
    return row

def add_shards(user_id: int, amount: int):
    shards, captures, badges = get_user(user_id)
    exec("UPDATE users SET shards=? WHERE user_id=?", (shards + amount, user_id))

def inc_captures(user_id: int, inc: int = 1):
    shards, captures, badges = get_user(user_id)
    exec("UPDATE users SET captures=? WHERE user_id=?", (captures + inc, user_id))

def record_capture(user_id: int, guild_id: int, name: str, series: str, rarity: str):
    exec("INSERT INTO captures (user_id, guild_id, name, series, rarity, ts) VALUES (?, ?, ?, ?, ?, ?)",
         (user_id, guild_id, name, series, rarity, int(time.time())))
