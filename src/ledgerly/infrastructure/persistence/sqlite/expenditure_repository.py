import pandas as pd
from ledgerly.domain.expenditure import Expenditure
from ledgerly.infrastructure.persistence.sqlite.connection import default_db

class SqliteExpenditureRepository:
    """지출 관련 Sqlite 저장소 구현체입니다."""

    def save_dataframe(self, df: pd.DataFrame):
        """기존 DataFrame 저장 방식 유지 (성능 및 호환성)"""
        with default_db.get_connection() as conn:
            df.to_sql(name="expenditure", con=conn, if_exists="append", index=False)

    def fetch_all(self) -> pd.DataFrame:
        with default_db.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM expenditure", conn)
