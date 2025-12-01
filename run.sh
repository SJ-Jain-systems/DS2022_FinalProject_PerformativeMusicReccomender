### Prerequisites

* Docker installed (e.g., Docker Desktop).
* Repo cloned locally.
* Optional: copy `.env.example` → `.env` and adjust any config variables if needed.

### Build

```bash
docker build -t performative-music-recommender:latest .
```

### Run

```bash
docker run --rm -p 9999:8080 --env-file .env performative-music-recommender:latest
```

* App UI: [http://localhost:9999/](http://localhost:9999/)
* Health check:

```bash
curl http://localhost:8080/health
```

### Usage Flow

1. Open `http://localhost:9999/`.
2. Click **“Load Music!”** to call `POST /ingest` and load the CSV into SQLite + build vectors.
3. In each of the 3 search boxes:
   * Start typing an **artist or title** (e.g., “Laufey”, “Big Thief”, "Clairo").
   * Pick from the dropdown (`Artist — Title`).
4. Click **“Recommend From My Taste”**.
5. See a result card with:

   * Artist — Title
   * Album, genre, tags, description
   * Similarity score.
