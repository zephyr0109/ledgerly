import pytest
import sqlite3
import pandas as pd
from ledgerly.infrastructure.persistence.sqlite.connection import SqliteDatabase
from ledgerly.infrastructure.persistence.sqlite.asset_repository import SqliteAssetRepository
from ledgerly.infrastructure.persistence.sqlite.debt_repository import SqliteDebtRepository
from ledgerly.domain.asset import AssetAccount, AssetSnapshot
from ledgerly.domain.debt import DebtAccount, DebtSnapshot
from datetime import date

@pytest.fixture
def in_memory_db(tmp_path):
    db_file = tmp_path / "test_ledgerly.db"
    db = SqliteDatabase(db_path=db_file)
    with db.get_connection() as conn:
        conn.execute("CREATE TABLE asset_account (asset_id TEXT PRIMARY KEY, asset_name TEXT, category TEXT, owner TEXT, memo TEXT, created_at TEXT, updated_at TEXT)")
        conn.execute("CREATE TABLE asset_snapshot (asset_id TEXT, snapshot_date TEXT, amount INTEGER, rate REAL)")
        conn.execute("CREATE TABLE debt_account (debt_id TEXT PRIMARY KEY, owner TEXT, debt_name TEXT, initial_principal INTEGER, repayment_type TEXT, maturity_date TEXT, updated_at TEXT)")
        conn.execute("CREATE TABLE debt_snapshot (debt_id TEXT, snapshot_date TEXT, principal_amount INTEGER, interest_rate REAL, accrued_interest INTEGER)")
    return db

def test_asset_repository_full(in_memory_db, monkeypatch):
    from ledgerly.infrastructure.persistence.sqlite import asset_repository
    monkeypatch.setattr(asset_repository, "default_db", in_memory_db)
    repo = SqliteAssetRepository()
    
    account = AssetAccount(asset_id="a1", asset_name="Asset1", category="c1", owner="o1")
    repo.upsert_account(account)
    assert len(repo.fetch_all_accounts()) == 1
    
    snapshot = AssetSnapshot(asset_id="a1", snapshot_date=date(2026,4,1), amount=100)
    repo.insert_snapshot(snapshot)

def test_debt_repository_full(in_memory_db, monkeypatch):
    from ledgerly.infrastructure.persistence.sqlite import debt_repository
    monkeypatch.setattr(debt_repository, "default_db", in_memory_db)
    repo = SqliteDebtRepository()
    
    debt = DebtAccount(debt_id="d1", owner="Me", debt_name="Loan", initial_principal=1000)
    repo.upsert_account(debt)
    
    snap = DebtSnapshot(debt_id="d1", snapshot_date=date(2026,4,1), principal_amount=900, interest_rate=2.0)
    repo.insert_snapshot(snap)
    
    status = repo.fetch_current_status()
    assert len(status) == 1
    assert status.iloc[0]["principal_amount"] == 900
