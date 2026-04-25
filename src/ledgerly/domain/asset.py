from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

@dataclass(frozen=True)
class AssetAccount:
    """자산 계정을 나타내는 도메인 모델입니다."""
    asset_id: str
    asset_name: str
    category: str
    owner: str
    memo: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass(frozen=True)
class AssetSnapshot:
    """특정 시점의 자산 잔액을 나타내는 도메인 모델입니다."""
    asset_id: str
    snapshot_date: date
    amount: int
    rate: Optional[float] = None
