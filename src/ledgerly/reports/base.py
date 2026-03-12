import sqlite3
import pandas as pd
from ledgerly.utils import find_project_root

PROJECT_ROOT = find_project_root()
DB_PATH = PROJECT_ROOT / 'data' / 'db' / 'ledgerly.db'
OUTPUT_DIR = PROJECT_ROOT / 'data' / 'output'

def get_connection():
    return sqlite3.connect(DB_PATH)

def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR
