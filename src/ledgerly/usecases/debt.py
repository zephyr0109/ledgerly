import pandas as pd
from ledgerly.domain.debt import DebtAccount, DebtSnapshot
from ledgerly.infrastructure.persistence.sqlite.debt_repository import SqliteDebtRepository

class DebtUseCase:
    """부채 관련 비즈니스 로직을 담당합니다."""
    
    def __init__(self, repository: SqliteDebtRepository = None):
        self.repository = repository or SqliteDebtRepository()

    def load_and_preprocess_account(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        df = df.rename(columns={
            "id": "debt_id", "소유주": "owner", "부채 이름": "debt_name",
            "원금": "initial_principal", "상환방식": "repayment_type", "만기일": "maturity_date"
        })
        df['maturity_date'] = pd.to_datetime(df['maturity_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        return df.where(pd.notnull(df), None)

    def load_and_preprocess_snapshot(self, file_path: str) -> pd.DataFrame:
        df = pd.read_csv(file_path)
        df = df.rename(columns={
            "id": "debt_id", "정산 날짜": "snapshot_date", "누적 이자": "accrued_interest",
            "이자율": "interest_rate", "원금 잔액": "principal_amount"
        })
        df['snapshot_date'] = pd.to_datetime(df['snapshot_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        return df.where(pd.notnull(df), None)

    def save_accounts(self, df: pd.DataFrame):
        for _, row in df.iterrows():
            account = DebtAccount(
                debt_id=row["debt_id"], owner=row["owner"], debt_name=row["debt_name"],
                initial_principal=int(row["initial_principal"]),
                repayment_type=row.get("repayment_type"),
                maturity_date=row.get("maturity_date")
            )
            self.repository.upsert_account(account)

    def save_snapshots(self, df: pd.DataFrame, force_date: str = None):
        for _, row in df.iterrows():
            snapshot = DebtSnapshot(
                debt_id=row["debt_id"],
                snapshot_date=force_date if force_date else row["snapshot_date"],
                principal_amount=int(row["principal_amount"]),
                interest_rate=float(row["interest_rate"]),
                accrued_interest=int(row["accrued_interest"]) if pd.notna(row["accrued_interest"]) else None
            )
            self.repository.insert_snapshot(snapshot)

    def get_current_status(self) -> pd.DataFrame:
        return self.repository.fetch_current_status()

    def generate_report(self, current_status_df: pd.DataFrame) -> pd.DataFrame:
        report_df = current_status_df.rename(columns={
            "debt_id": "부채ID", "owner": "소유주", "debt_name": "부채 이름",
            "initial_principal": "최초 원금", "principal_amount": "남은 원금",
            "interest_rate": "이자율(%)", "accrued_interest": "누적 이자", "snapshot_date": "정산 날짜"
        })
        total_row = {
            "부채ID": "", "소유주": "", "부채 이름": "총계", "최초 원금": "",
            "남은 원금": report_df["남은 원금"].sum(), "이자율(%)": "", "누적 이자": "", "정산 날짜": ""
        }
        return pd.concat([report_df, pd.DataFrame([total_row])], ignore_index=True)
