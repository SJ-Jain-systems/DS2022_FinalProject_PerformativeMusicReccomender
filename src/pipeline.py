import logging
import pandas as pd
import pickle

from .config import DATA_PATH
from .db import init_db, clear_tables, insert_items, insert_vectors
from .recommender import build_tfidf, to_bytes

logger = logging.getLogger(__name__)

def run_pipeline():
    """
    ETL + vector build:
    1) load CSV
    2) clean/normalize
    3) build TF-IDF vectors
    4) store items + vectors in SQLite
    """
    logger.info("Pipeline start")
    df = pd.read_csv(DATA_PATH)

    required = {"item_id","title","artist","album","genre","tags","description"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # clean
    df = df.dropna(subset=["item_id","title"])
    df["item_id"] = df["item_id"].astype(int)

    for col in ["artist","album","genre","tags","description"]:
        df[col] = df[col].fillna("").astype(str)

    # MUSIC text blob
    df["text_blob"] = (
        df["title"] + " " +
        df["artist"] + " " +
        df["album"] + " " +
        df["genre"] + " " +
        df["tags"] + " " +
        df["description"]
    )

    init_db()
    clear_tables()
    insert_items(df)

    vectorizer, X = build_tfidf(df["text_blob"].tolist())

    vectors = []
    for item_id, row in zip(df["item_id"].tolist(), X):
        vectors.append((int(item_id), to_bytes(row)))

    insert_vectors(vectors)

    # persist vectorizer (optional but nice)
    with open("assets/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    logger.info("Pipeline complete: %d songs inserted", len(df))
    return len(df)
