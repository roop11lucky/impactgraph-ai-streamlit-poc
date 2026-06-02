import json
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_entities() -> pd.DataFrame:
    with open(DATA_DIR / "entities.json", "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

def load_dependencies() -> pd.DataFrame:
    with open(DATA_DIR / "dependencies.json", "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

def load_test_cases() -> pd.DataFrame:
    with open(DATA_DIR / "test_cases.json", "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))