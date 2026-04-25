from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass(frozen=True)
class DebtAccount:
    """부채 계정을 나타내는 도메인 모델입니다."""
    debt_id: str
    owner: str
    debt_name: str
    initial_principal: int
    repayment_type: Optional[str] = None
    maturity_date: Optional[date] = None
    updated_at: Optional[datetime] = None

@dataclass(frozen=True)
class DebtSnapshot:
    """특정 시점의 부채 잔액 및 이자 상태를 나타내는 도메인 모델입니다."""
    debt_id: str
    snapshot_date: date
    principal_amount: int
    interest_rate: float
    accrued_interest: Optional[int] = None
