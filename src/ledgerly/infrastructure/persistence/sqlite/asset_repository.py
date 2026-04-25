import pandas as pd
from typing import List, Optional
from ledgerly.domain.asset import AssetAccount, AssetSnapshot
from ledgerly.infrastructure.persistence.sqlite.connection import default_db

class SqliteAssetRepository:
    """자산 관련 Sqlite 저장소 구현체입니다."""

    def upsert_account(self, account: AssetAccount):
        upsert_sql = """
            INSERT INTO asset_account (asset_id, asset_name, category, owner, memo, created_at, updated_at)
            VALUES (:asset_id, :asset_name, :category, :owner, :memo, datetime('now'), datetime('now'))
            ON CONFLICT(asset_id) DO UPDATE SET
                asset_name = excluded.asset_name,
                category = excluded.category,
                owner = excluded.owner,
                memo = excluded.memo,
                updated_at = datetime('now');
        """
        with default_db.get_connection() as conn:
            conn.execute(upsert_sql, {
                "asset_id": account.asset_id,
                "asset_name": account.asset_name,
                "category": account.category,
                "owner": account.owner,
                "memo": account.memo
            })

    def insert_snapshot(self, snapshot: AssetSnapshot):
        insert_sql = """
            INSERT INTO asset_snapshot (asset_id, snapshot_date, amount, rate)
            VALUES (:asset_id, :snapshot_date, :amount, :rate);
        """
        with default_db.get_connection() as conn:
            conn.execute(insert_sql, {
                "asset_id": snapshot.asset_id,
                "snapshot_date": snapshot.snapshot_date,
                "amount": snapshot.amount,
                "rate": snapshot.rate
            })

    def fetch_all_accounts(self) -> pd.DataFrame:
        with default_db.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM asset_account", conn)
