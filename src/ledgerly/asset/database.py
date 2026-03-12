import sqlite3
import pandas as pd
from ledgerly.utils import find_project_root

PROJECT_ROOT = find_project_root()
DB_PATH = PROJECT_ROOT / 'data' / 'db' / 'ledgerly.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def upsert_asset_accounts(account_df: pd.DataFrame):
    """Update or insert asset account records."""
    upsert_sql = """

        INSERT INTO asset_account (
            asset_id,
            asset_name,
            category,
            owner,
            memo,
            created_at,
            updated_at
        )
        VALUES (
            :asset_id,
            :asset_name,
            :category,
            :owner,
            :memo,
            datetime('now'),
            datetime('now')
        )
        ON CONFLICT(asset_id) DO UPDATE SET
            asset_name = excluded.asset_name,
            category   = excluded.category,
            owner      = excluded.owner,
            memo       = excluded.memo,
            updated_at = datetime('now');

    """
    with get_connection() as conn:
        cursor = conn.cursor()
        for _, row in account_df.iterrows():
            print(row)
            cursor.execute(upsert_sql, {
                "asset_id": row["asset_id"],
                "asset_name": row["asset_name"],
                "category": row["category"],
                "owner": row["owner"],
                "memo": row["memo"]
            })
        conn.commit()


def insert_asset_snapshots(snapshot_df: pd.DataFrame):
    """Insert asset snapshot records."""
    snapshot_insert_sql = """
        insert into asset_snapshot (
            asset_id,
            snapshot_date,
            amount,
            rate
        ) values (
            :asset_id,
            :snapshot_date,
            :amount,
            :rate
            );
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        for _, row in snapshot_df.iterrows():
            print(row)
            cursor.execute(snapshot_insert_sql, {
                "asset_id": row["asset_id"],
                "snapshot_date": row["snapshot_date"],
                "amount": row["amount"],
                "rate": row.get("rate", None)
            })

        conn.commit()
