from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

@dataclass(frozen=True)
class Expenditure:
    """지출 내역을 나타내는 도메인 모델입니다."""
    used_at: date
    payment_type: str
    merchant_name: str
    installment_type: str  # 'single', 'installment'
    amount: int
    category: str
    payment_provider: Optional[str] = None
    remaining_amount: int = 0
    memo: Optional[str] = None
    source_uid: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        # 비즈니스 규칙 검증
        if self.amount < 0:
            raise ValueError("지출 금액은 0보다 커야 합니다.")
        if self.installment_type not in ('single', 'installment'):
            raise ValueError("결제 방식은 'single' 또는 'installment'여야 합니다.")
