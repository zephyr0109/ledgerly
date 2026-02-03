import re
import pandas as pd


from ledgerly.utils import find_project_root

PROJECT_ROOT = find_project_root()

mapping_path = PROJECT_ROOT / "data" / "resources" / "expenditure_mapping.csv"
# mapping_path.exists()

mapping_df = pd.read_csv(mapping_path)
mapping_df = mapping_df.sort_values("priority").reset_index(drop=True)
mapping_df.head()



def map_category(merchant_name: str, mapping_df:pd.DataFrame = mapping_df) -> str | None:
    if pd.isna(merchant_name) or merchant_name == "":
        return None
    for _, row in mapping_df.iterrows():
        match_type = row["match_type"]
        pattern = row["pattern"]
        category = row["category"]
        if match_type == "exact":
            if merchant_name == pattern:
                return category
        elif match_type == "contains":
            if pattern in merchant_name:
                return category
        elif match_type == "regex":
            if re.search(pattern, merchant_name):
                return category
    return None
