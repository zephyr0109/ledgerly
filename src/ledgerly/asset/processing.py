import pandas as pd
from typing import Tuple

def load_and_preprocess_asset_account(account_path:str) -> pd.DataFrame:
    """Load CSV files and preprocess them for database insertion."""
    account_df = pd.read_csv(account_path)
    account_df = account_df.rename(columns={
        "ID": "asset_id",
        "자산이름": "asset_name",
        "분류": "category",
        "소유주": "owner",
        "비고": "memo"
    })
    account_df = account_df.where(pd.notnull(account_df), None )
    return account_df

def load_and_preprocess_asset_snapshot(snapshot_path:str) -> pd.DataFrame:
    """Load CSV files and preprocess them for database insertion."""
    snapshot_df = pd.read_csv(snapshot_path)
    snapshot_df = snapshot_df.rename(columns={
        "ID": "asset_id",
        "정산일": "snapshot_date",
        "금액": "amount",
        "이율/수익률" : "rate"
    })
    snapshot_df = snapshot_df.where(pd.notnull(snapshot_df), None)
    return snapshot_df
