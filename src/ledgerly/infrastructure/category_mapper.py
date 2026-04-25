import pandas as pd
from ledgerly.utils import find_project_root

PROJECT_ROOT = find_project_root()
RESOURCE_DIR = PROJECT_ROOT / "data" / "resources"
MAPPING_FILE = RESOURCE_DIR / "expenditure_mapping.csv"

def load_mapping_data():
    if not MAPPING_FILE.exists():
        return pd.DataFrame(columns=["merchant_name", "category"])
    return pd.read_csv(MAPPING_FILE)

def map_category(merchant_name: str) -> str:
    mapping_df = load_mapping_data()
    match = mapping_df[mapping_df["merchant_name"] == merchant_name]
    if not match.empty:
        return match.iloc[0]["category"]
    return "미분류"
