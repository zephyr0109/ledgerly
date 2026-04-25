import pytest
import pandas as pd
from unittest.mock import MagicMock
from ledgerly.usecases.asset import AssetUseCase
from ledgerly.usecases.debt import DebtUseCase
from ledgerly.domain.asset import AssetAccount

def test_asset_usecase_preprocessing(tmp_path):
    csv_file = tmp_path / "asset.csv"
    content = "ID,자산이름,분류,소유주,비고\ntest_id,Test Asset,bank,Me,memo"
    csv_file.write_text(content, encoding='utf-8')
    usecase = AssetUseCase(repository=MagicMock())
    df = usecase.load_and_preprocess_account(str(csv_file))
    assert df.iloc[0]["asset_id"] == "test_id"

def test_asset_usecase_save_logic():
    mock_repo = MagicMock()
    usecase = AssetUseCase(repository=mock_repo)
    df = pd.DataFrame([{"asset_id": "a1", "asset_name": "N", "category": "C", "owner": "O", "memo": None}])
    usecase.save_accounts(df)
    assert mock_repo.upsert_account.called
    snap_df = pd.DataFrame([{"asset_id": "a1", "snapshot_date": "2026-04-01", "amount": 100, "rate": 1.0}])
    usecase.save_snapshots(snap_df)
    assert mock_repo.insert_snapshot.called

def test_debt_usecase_full(tmp_path):
    csv_file = tmp_path / "debt.csv"
    csv_file.write_text("id,소유주,부채 이름,원금,상환방식,만기일\nd1,Me,Loan,1000,type,2026-12-31", encoding='utf-8')
    mock_repo = MagicMock()
    usecase = DebtUseCase(repository=mock_repo)
    
    df = usecase.load_and_preprocess_account(str(csv_file))
    assert df.iloc[0]["debt_id"] == "d1"
    
    usecase.save_accounts(df)
    assert mock_repo.upsert_account.called

    snap_df = pd.DataFrame([{"debt_id": "d1", "snapshot_date": "2026-04-01", "principal_amount": 900, "interest_rate": 2.0, "accrued_interest": 10}])
    usecase.save_snapshots(snap_df)
    assert mock_repo.insert_snapshot.called

def test_debt_usecase_report():
    mock_repo = MagicMock()
    mock_df = pd.DataFrame([{"debt_id": "d1", "owner": "O", "debt_name": "N", "initial_principal": 100, "principal_amount": 80, "interest_rate": 3.0, "accrued_interest": 5, "snapshot_date": "2026-04-25"}])
    mock_repo.fetch_current_status.return_value = mock_df
    usecase = DebtUseCase(repository=mock_repo)
    report = usecase.generate_report(usecase.get_current_status())
    assert len(report) == 2
    assert report.iloc[1]["부채 이름"] == "총계"
