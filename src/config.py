import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "assets" / "recs.db"))
DATA_PATH = os.getenv("DATA_PATH", str(BASE_DIR / "assets" / "music.csv"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# recommender settings
MAX_FEATURES = int(os.getenv("MAX_FEATURES", 5000))
N_RECS_DEFAULT = int(os.getenv("N_RECS_DEFAULT", 5))
