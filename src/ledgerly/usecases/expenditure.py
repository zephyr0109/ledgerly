import pandas as pd
from datetime import datetime
from ledgerly.domain.expenditure import Expenditure
from ledgerly.infrastructure.persistence.sqlite.expenditure_repository import SqliteExpenditureRepository

class ExpenditureUseCase:
    """지출 관련 비즈니스 로직을 담당합니다."""
    
    def __init__(self, repository: SqliteExpenditureRepository = None):
        self.repository = repository or SqliteExpenditureRepository()

    def import_from_dataframe(self, df: pd.DataFrame):
        self.repository.save_dataframe(df)

    def get_all_expenditures(self) -> pd.DataFrame:
        return self.repository.fetch_all()

    def add_manual_expenditure(self, expenditure: Expenditure):
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
        self.repository.save_dataframe(df)
