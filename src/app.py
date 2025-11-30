# src/app.py

from flask import Flask, jsonify, request, render_template
import logging
from pathlib import Path

from scipy.sparse import vstack

from .config import LOG_LEVEL, N_RECS_DEFAULT
from .pipeline import run_pipeline
from .db import init_db, read_items, read_item, read_vectors
from .recommender import from_bytes, recommend_for, recommend_from_likes


def create_app():
    # Point Flask to /app/templates and /app/static inside Docker
    base_dir = Path(__file__).resolve().parent  # /app/src
    app = Flask(
        __name__,
        template_folder=str(base_dir.parent / "templates"),
        static_folder=str(base_dir.parent / "static"),
        static_url_path="/static",
    )

    logging.basicConfig(level=getattr(logging, LOG_LEVEL))
    logger = logging.getLogger("mini-music-recommender")

    @app.get("/")
    def home():
        return render_template("index.html")

    init_db()

    def load_matrix():
        vectors = read_vectors()
        if not vectors:
            return [], None
        item_ids = [iid for iid, _ in vectors]
        rows = [from_bytes(b) for _, b in vectors]
        matrix = vstack(rows)
        return item_ids, matrix

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/ingest")
    def ingest():
        n = run_pipeline()
        return jsonify({"inserted_songs": n})

    @app.get("/songs")
    def songs():
        rows = read_items()
        out = [
            {
                "item_id": r[0],
                "title": r[1],
                "artist": r[2],
                "album": r[3],
                "genre": r[4],
                "tags": r[5],
                "description": r[6],
            }
            for r in rows
        ]
        return jsonify(out)

    @app.get("/recommend")
    def recommend():
        item_id = request.args.get("item_id", type=int)
        top_n = request.args.get("n", default=N_RECS_DEFAULT, type=int)

        if item_id is None:
            return jsonify({"error": "item_id query param required"}), 400

        item_ids, matrix = load_matrix()
        if matrix is None:
            return jsonify({"error": "database empty. POST /ingest first"}), 400

        recs = recommend_for(item_id, item_ids, matrix, top_n=top_n)

        enriched = []
        for rid, score in recs:
            it = read_item(rid)
            if it:
                enriched.append(
                    {
                        "item_id": rid,
                        "title": it[1],
                        "artist": it[2],
                        "album": it[3],
                        "genre": it[4],
                        "tags": it[5],
                        "description": it[6],
                        "score": score,
                    }
                )

        return jsonify({"for_item_id": item_id, "recommendations": enriched})

    @app.get("/search")
    def search():
        q = request.args.get("q", default="", type=str).lower()
        if not q:
            return jsonify({"error": "q query param required"}), 400

        rows = read_items()
        hits = []
        for r in rows:
            blob = " ".join([str(x or "") for x in r]).lower()
            if q in blob:
                hits.append({"item_id": r[0], "title": r[1], "artist": r[2]})
        return jsonify({"query": q, "hits": hits})

    @app.post("/recommend_from_likes")
    def recommend_from_likes_route():
        """
        Expects JSON like:
        {
          "likes": [1, 5, 10]
        }
        """
        body = request.get_json(silent=True) or {}
        likes = body.get("likes", [])

        # Must be a non-empty list
        if not isinstance(likes, list) or len(likes) == 0:
            return jsonify({"error": "likes must be a non-empty list"}), 400

        # must not contain duplicates
        if len(likes) != len(set(likes)):
            return jsonify({"error": "Please choose 3 different songs (no duplicates)."}), 400

        # require exactly 3 songs
        if len(likes) != 3:
            return jsonify({"error": "Please select exactly 3 songs."}), 400

        item_ids, matrix = load_matrix()
        if matrix is None:
            return jsonify({"error": "database empty. POST /ingest first"}), 400
        # ask for more than 1 so we have backups
        raw_recs = recommend_from_likes(likes, item_ids, matrix, top_n=10)

        # filter out any songs the user already selected
        filtered = [(rid, score) for rid, score in raw_recs if rid not in likes]

        if not filtered:
            return jsonify({"error": "No new songs to recommend (all results were songs you already picked)."}), 400

        best_id, best_score = filtered[0]
        it = read_item(best_id)

        # Rescale cosine similarity for display
        display_score = min(best_score * 2.2, 0.99)

        return jsonify(
            {
                "liked_item_ids": likes,
                "recommendation": {
                    "item_id": best_id,
                    "title": it[1],
                    "artist": it[2],
                    "album": it[3],
                    "genre": it[4],
                    "tags": it[5],
                    "description": it[6],
                    "score": display_score,   # shown to user
                    "raw_score": best_score,  # real cosine, for debugging
                },
            }
        )


    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
