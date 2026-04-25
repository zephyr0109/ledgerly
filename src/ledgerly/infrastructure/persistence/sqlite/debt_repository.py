import pandas as pd
from ledgerly.domain.debt import DebtAccount, DebtSnapshot
from ledgerly.infrastructure.persistence.sqlite.connection import default_db

class SqliteDebtRepository:
    """부채 관련 Sqlite 저장소 구현체입니다."""

    def upsert_account(self, account: DebtAccount):
        upsert_sql = """
            INSERT INTO debt_account (debt_id, owner, debt_name, initial_principal, repayment_type, maturity_date, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(debt_id) DO UPDATE SET
                owner = excluded.owner,
                debt_name = excluded.debt_name,
                initial_principal = excluded.initial_principal,
                repayment_type = excluded.repayment_type,
                updated_at = datetime('now');
        """
        with default_db.get_connection() as conn:
            conn.execute(upsert_sql, (
                account.debt_id,
                account.owner,
                account.debt_name,
                account.initial_principal,
                account.repayment_type,
                account.maturity_date
            ))

    def insert_snapshot(self, snapshot: DebtSnapshot):
        insert_sql = """
            INSERT INTO debt_snapshot (debt_id, snapshot_date, principal_amount, interest_rate, accrued_interest)
            VALUES (?, ?, ?, ?, ?);
        """
        with default_db.get_connection() as conn:
            conn.execute(insert_sql, (
                snapshot.debt_id,
                snapshot.snapshot_date,
                snapshot.principal_amount,
                snapshot.interest_rate,
                snapshot.accrued_interest
            ))

    def fetch_current_status(self) -> pd.DataFrame:
        select_sql = """
            SELECT da.debt_id, da.owner, da.debt_name, da.initial_principal,
                   ds.principal_amount, ds.interest_rate, ds.accrued_interest, ds.snapshot_date
            FROM debt_account da
            JOIN debt_snapshot ds ON da.debt_id = ds.debt_id
            WHERE ds.snapshot_date = (
                SELECT MAX(snapshot_date) FROM debt_snapshot WHERE debt_id = da.debt_id
            )
            ORDER BY da.owner, da.debt_id;
        """
        with default_db.get_connection() as conn:
            return pd.read_sql_query(select_sql, conn)
