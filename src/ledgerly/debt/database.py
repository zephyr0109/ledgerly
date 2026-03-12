import sqlite3
import pandas as pd
from ledgerly.utils import find_project_root

PROJECT_ROOT = find_project_root()
DB_PATH = PROJECT_ROOT / 'data' / 'db' / 'ledgerly.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def upsert_debt_accounts(account_df: pd.DataFrame):
    """Update or insert debt account records."""
    upsert_sql = """
    INSERT INTO debt_account(
        debt_id,
        owner,
        debt_name,
        initial_principal,
        repayment_type,
        maturity_date,
        updated_at
        )
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(debt_id) DO UPDATE SET
        owner = excluded.owner,
        debt_name = excluded.debt_name,
        initial_principal = excluded.initial_principal,
        repayment_type = excluded.repayment_type,
        updated_at = datetime('now');
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        for _, row in account_df.iterrows():
            cursor.execute(upsert_sql, (
                row["debt_id"],
                row["owner"],
                row["debt_name"],
                int(row["initial_principal"]),
                row.get("repayment_type"),
                row.get("maturity_date")
            ))
        conn.commit()

def insert_debt_snapshots(snapshot_df: pd.DataFrame, force_date: str = None):
    """Insert debt snapshot records."""
    snapshot_insert_sql = """
    INSERT INTO debt_snapshot (
        debt_id,
        snapshot_date,
        principal_amount,
        interest_rate,
        accrued_interest
        )
    VALUES (?, ?, ?, ?, ?);
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        for _, row in snapshot_df.iterrows():
            snapshot_date = force_date if force_date else row["snapshot_date"]
            cursor.execute(snapshot_insert_sql, (
                row["debt_id"],
                snapshot_date,
                int(row["principal_amount"]),
                float(row["interest_rate"]),
                int(row["accrued_interest"]) if pd.notna(row["accrued_interest"]) else None
            ))
        conn.commit()

def fetch_current_debt_status() -> pd.DataFrame:
    """Fetch current status of all debts."""
    select_sql = """
    SELECT
        da.debt_id,
        da.owner,
        da.debt_name,
        da.initial_principal,
        ds.principal_amount,
        ds.interest_rate,
        ds.accrued_interest,
        ds.snapshot_date
    FROM debt_account da
    JOIN debt_snapshot ds ON da.debt_id = ds.debt_id
    WHERE
    ds.snapshot_date = (
        SELECT MAX(snapshot_date)
        FROM debt_snapshot
        WHERE debt_id = da.debt_id
    )
    ORDER BY da.owner, da.debt_id;
    """
    with get_connection() as conn:
        return pd.read_sql_query(select_sql, conn)
