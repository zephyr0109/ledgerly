import pytest
from datetime import date
from ledgerly.domain.expenditure import Expenditure
from ledgerly.domain.asset import AssetAccount
from ledgerly.domain.debt import DebtAccount

def test_expenditure_validation():
    # 정상 케이스
    exp = Expenditure(
        used_at=date(2026, 4, 25),
        payment_type="card",
        merchant_name="Test Store",
        installment_type="single",
        amount=10000,
        category="food"
    )
    assert exp.amount == 10000

    # 금액 오류 케이스
    with pytest.raises(ValueError, match="지출 금액은 0보다 커야 합니다."):
        Expenditure(
            used_at=date(2026, 4, 25),
            payment_type="card",
            merchant_name="Test Store",
            installment_type="single",
            amount=-1,
            category="food"
        )

    # 결제 방식 오류 케이스
    with pytest.raises(ValueError, match="결제 방식은 'single' 또는 'installment'여야 합니다."):
        Expenditure(
            used_at=date(2026, 4, 25),
            payment_type="card",
            merchant_name="Test Store",
            installment_type="invalid",
            amount=10000,
            category="food"
        )

def test_asset_account_creation():
    account = AssetAccount(
        asset_id="test_id",
        asset_name="Test Asset",
        category="bank",
        owner="owner"
    )
    assert account.asset_id == "test_id"

def test_debt_account_creation():
    debt = DebtAccount(
        debt_id="debt_id",
        owner="owner",
        debt_name="Debt Name",
        initial_principal=1000000
    )
    assert debt.initial_principal == 1000000
