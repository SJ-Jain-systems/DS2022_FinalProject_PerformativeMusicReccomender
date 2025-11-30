import sqlite3
from contextlib import contextmanager
from .config import DB_PATH

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT,
            album TEXT,
            genre TEXT,
            tags TEXT,
            description TEXT,
            text_blob TEXT
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS vectors (
            item_id INTEGER PRIMARY KEY,
            vector BLOB NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(item_id)
        );
        """)
        conn.commit()

def clear_tables():
    with get_conn() as conn:
        conn.execute("DELETE FROM vectors;")
        conn.execute("DELETE FROM items;")
        conn.commit()

def insert_items(df):
    rows = df[
        ["item_id","title","artist","album","genre","tags","description","text_blob"]
    ].values.tolist()

    with get_conn() as conn:
        conn.executemany("""
        INSERT INTO items(item_id,title,artist,album,genre,tags,description,text_blob)
        VALUES(?,?,?,?,?,?,?,?);
        """, rows)
        conn.commit()

def insert_vectors(pairs):
    # pairs: [(item_id, vector_bytes), ...]
    with get_conn() as conn:
        conn.executemany("""
        INSERT INTO vectors(item_id, vector)
        VALUES(?,?);
        """, pairs)
        conn.commit()

def read_items():
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT item_id, title, artist, album, genre, tags, description
            FROM items;
        """)
        return cur.fetchall()

def read_item(item_id):
    with get_conn() as conn:
        cur = conn.execute("""
        SELECT item_id, title, artist, album, genre, tags, description, text_blob
        FROM items WHERE item_id=?;
        """, (item_id,))
        return cur.fetchone()

def read_vectors():
    with get_conn() as conn:
        cur = conn.execute("SELECT item_id, vector FROM vectors;")
        return cur.fetchall()
