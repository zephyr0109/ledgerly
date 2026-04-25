from ledgerly.usecases.asset import AssetUseCase

_usecase = AssetUseCase()

def upsert_asset_accounts(account_df):
    return _usecase.save_accounts(account_df)

def insert_asset_snapshots(snapshot_df):
    return _usecase.save_snapshots(snapshot_df)

def load_and_preprocess_asset_account(account_path):
    return _usecase.load_and_preprocess_account(account_path)

def load_and_preprocess_asset_snapshot(snapshot_path):
    return _usecase.load_and_preprocess_snapshot(snapshot_path)

__all__ = [
    "upsert_asset_accounts",
    "insert_asset_snapshots",
    "load_and_preprocess_asset_account",
    "load_and_preprocess_asset_snapshot",
]
