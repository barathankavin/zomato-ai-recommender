import os
from pathlib import Path

# Root of the project (assuming paths.py is in src/milestone1/phase0/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Data directory for storing downloaded datasets/cache
DATA_DIR = PROJECT_ROOT / "data"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)
