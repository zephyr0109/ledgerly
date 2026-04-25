import pandas as pd
from ledgerly.domain.asset import AssetAccount, AssetSnapshot
from ledgerly.infrastructure.persistence.sqlite.asset_repository import SqliteAssetRepository

class AssetUseCase:
    """자산 관련 비즈니스 로직을 담당합니다."""
    
    def __init__(self, repository: SqliteAssetRepository = None):
        self.repository = repository or SqliteAssetRepository()

    def load_and_preprocess_account(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        df = df.rename(columns={
            "ID": "asset_id", "자산이름": "asset_name", "분류": "category",
            "소유주": "owner", "비고": "memo"
        })
        return df.where(pd.notnull(df), None)

    def load_and_preprocess_snapshot(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        df = df.rename(columns={
            "ID": "asset_id", "정산일": "snapshot_date", "금액": "amount", "이율/수익률": "rate"
        })
        return df.where(pd.notnull(df), None)

    def save_accounts(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            account = AssetAccount(
                asset_id=row["asset_id"], asset_name=row["asset_name"],
                category=row["category"], owner=row["owner"], memo=row["memo"]
            )
            self.repository.upsert_account(account)

    def save_snapshots(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            snapshot = AssetSnapshot(
                asset_id=row["asset_id"], snapshot_date=row["snapshot_date"],
                amount=row["amount"], rate=row.get("rate")
            )
            self.repository.insert_snapshot(snapshot)
