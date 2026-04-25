from ledgerly.usecases.debt import DebtUseCase

_usecase = DebtUseCase()

def load_and_preprocess_debt_account(account_path):
    return _usecase.load_and_preprocess_account(account_path)

def load_and_preprocess_debt_snapshot(snapshot_path):
    return _usecase.load_and_preprocess_snapshot(snapshot_path)

def upsert_debt_accounts(account_df):
    return _usecase.save_accounts(account_df)

def insert_debt_snapshots(snapshot_df, force_date=None):
    return _usecase.save_snapshots(snapshot_df, force_date=force_date)

def fetch_current_debt_status():
    return _usecase.get_current_status()

def generate_debt_report(current_status_df):
    return _usecase.generate_report(current_status_df)

__all__ = [
    "fetch_current_debt_status",
    "upsert_debt_accounts",
    "insert_debt_snapshots",
    "load_and_preprocess_debt_account",
    "load_and_preprocess_debt_snapshot",
    "generate_debt_report",
]
