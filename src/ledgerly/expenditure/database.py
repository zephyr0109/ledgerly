import sqlite3
import pandas as pd

from ledgerly.utils import find_project_root

PROJECT_ROOT = find_project_root()


db_path = PROJECT_ROOT / "data" / "db"/ "ledgerly.db"
conn = sqlite3.connect(db_path)

def insert_expenditure_data(expenditure_df: pd.DataFrame):
    """가계부 지출 데이터프레임을 데이터베이스에 삽입합니다."""
    expenditure_df.to_sql(
        name="expenditure",
        con=conn,
        if_exists="append",
        index=False
    )

def fetch_expenditure_data() -> pd.DataFrame:
    """데이터베이스에서 가계부 지출 데이터를 조회하여 데이터프레임으로 반환합니다."""
    query = "SELECT * FROM expenditure"
    expenditure_df = pd.read_sql_query(query, conn)
    return expenditure_df