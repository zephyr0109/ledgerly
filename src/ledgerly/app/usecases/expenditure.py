from datetime import datetime
from typing import List
import pandas as pd
from ledgerly.domain.expenditure import Expenditure
from ledgerly.expenditure.database import insert_expenditure_data, fetch_expenditure_data

class ExpenditureUseCase:
    """지출 내역 관련 비즈니스 로직을 담당하는 유스케이스 레이어입니다."""

    def import_from_dataframe(self, df: pd.DataFrame):
        """데이터프레임 형태의 지출 내역을 DB에 저장합니다. (기존 로직 래핑)"""
        # TODO: 추후 도메인 모델 검증 로직 추가 가능
        insert_expenditure_data(df)

    def get_all_expenditures(self) -> pd.DataFrame:
        """모든 지출 내역을 조회합니다."""
        return fetch_expenditure_data()

    def add_manual_expenditure(self, expenditure: Expenditure):
        """수동으로 지출 내역을 추가합니다. (UI에서 사용 예정)"""
        # 도메인 모델을 dict나 df로 변환하여 저장
        data = {
            "used_at": [expenditure.used_at],
            "payment_type": [expenditure.payment_type],
            "payment_provider": [expenditure.payment_provider],
            "merchant_name": [expenditure.merchant_name],
            "installment_type": [expenditure.installment_type],
            "amount": [expenditure.amount],
            "remaining_amount": [expenditure.remaining_amount],
            "category": [expenditure.category],
            "memo": [expenditure.memo],
            "source_uid": [expenditure.source_uid or f"manual_{datetime.now().timestamp()}"],
        }
        df = pd.DataFrame(data)
        insert_expenditure_data(df)
