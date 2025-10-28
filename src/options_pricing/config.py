import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()
RAW_DIR = DATA_DIR / "raw"
QA_DIR = DATA_DIR / "qa"

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
if not POLYGON_API_KEY:
    raise RuntimeError("POLYGON_API_KEY missing. Put it in .env")

RAW_DIR.mkdir(parents=True, exist_ok=True)
(QA_DIR / "indices").mkdir(parents=True, exist_ok=True)
(RAW_DIR / "indices").mkdir(parents=True, exist_ok=True)
