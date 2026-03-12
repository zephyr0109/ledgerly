import pandas as pd
from typing import Tuple

def load_and_preprocess_debt_data(account_path: str, snapshot_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load CSV files and preprocess them for database insertion."""
    account_df = pd.read_csv(account_path)
    snapshot_df = pd.read_csv(snapshot_path)
    
    account_df = account_df.rename(columns={
        "id": "debt_id",
        "소유주": "owner",
        "부채 이름": "debt_name",
        "원금": "initial_principal",
        "상환방식": "repayment_type",
        "만기일": "maturity_date"
    })
    
    snapshot_df = snapshot_df.rename(columns={
        "id": "debt_id",
        "정산 날짜": "snapshot_date",
        "누적 이자": "accrued_interest",
        "이자율": "interest_rate",
        "원금 잔액": "principal_amount"
    })
    
    snapshot_df['snapshot_date'] = pd.to_datetime(snapshot_df['snapshot_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    account_df['maturity_date'] = pd.to_datetime(account_df['maturity_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    
    return account_df, snapshot_df

def generate_debt_report(current_status_df: pd.DataFrame) -> pd.DataFrame:
    """Generate a formatted report DataFrame from current status."""
    report_df = current_status_df.rename(columns={
        "debt_id": "부채ID",
        "owner": "소유주",
        "debt_name": "부채 이름",
        "initial_principal": "최초 원금",
        "principal_amount": "남은 원금",
        "interest_rate": "이자율(%)",
        "accrued_interest": "누적 이자",
        "snapshot_date": "정산 날짜"
    })
    
    total_row = {
        "부채ID": "",
        "소유주": "",
        "부채 이름": "총계",
        "최초 원금": "",
        "남은 원금": report_df["남은 원금"].sum(),
        "이자율(%)": "",
        "누적 이자": "",
        "정산 날짜": ""
    }
    
    report_df = pd.concat(
        [report_df, pd.DataFrame([total_row])],
        ignore_index=True
    )
    return report_df
