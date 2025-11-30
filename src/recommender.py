# src/recommender.py

import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import MAX_FEATURES


def build_tfidf(texts):
    """
    Build TF-IDF vectorizer + matrix from a list of text blobs.
    Returns (vectorizer, X) where X is a sparse matrix aligned to texts order.
    """
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=MAX_FEATURES
    )
    X = vectorizer.fit_transform(texts)
    return vectorizer, X


def to_bytes(sparse_row):
    """Serialize a sparse row vector to bytes for SQLite storage."""
    return pickle.dumps(sparse_row)


def from_bytes(b):
    """Deserialize bytes back into a sparse row vector."""
    return pickle.loads(b)


def recommend_for(item_id, all_item_ids, matrix, top_n=5):
    """
    Standard content-based recommendation for a single item.

    item_id: int
    all_item_ids: list[int] aligned to matrix rows
    matrix: sparse TF-IDF matrix
    top_n: number of recs

    Returns: list of (recommended_item_id, similarity_score)
    """
    idx_map = {iid: i for i, iid in enumerate(all_item_ids)}
    if item_id not in idx_map:
        return []

    i = idx_map[item_id]
    sims = cosine_similarity(matrix[i], matrix).flatten()
    order = np.argsort(-sims)

    recs = []
    for j in order:
        rid = int(all_item_ids[j])
        if rid == item_id:
            continue
        recs.append((rid, float(sims[j])))
        if len(recs) >= top_n:
            break
    return recs


def recommend_from_likes(like_ids, all_item_ids, matrix, top_n=1):
    """
    NEW FEATURE:
    Given a list of liked song IDs (e.g., 3 songs),
    build a "taste profile" by averaging their TF-IDF vectors,
    then recommend the best matching song not already liked.

    like_ids: list[int]
    all_item_ids: list[int] aligned to matrix rows
    matrix: sparse TF-IDF matrix
    top_n: number of recs to return (default 1)

    Returns: list of (recommended_item_id, similarity_score)
    """
    idx_map = {iid: i for i, iid in enumerate(all_item_ids)}

    # keep only valid IDs that exist in the matrix
    like_ids = [int(iid) for iid in like_ids if int(iid) in idx_map]
    if len(like_ids) == 0:
        return []

    like_rows = [matrix[idx_map[iid]] for iid in like_ids]

    # average the liked vectors into one profile
    taste_vec = like_rows[0]
    for r in like_rows[1:]:
        taste_vec = taste_vec + r
    taste_vec = taste_vec / len(like_rows)

    sims = cosine_similarity(taste_vec, matrix).flatten()
    order = np.argsort(-sims)

    recs = []
    for j in order:
        rid = int(all_item_ids[j])
        if rid in like_ids:
            continue
        recs.append((rid, float(sims[j])))
        if len(recs) >= top_n:
            break
    return recs
