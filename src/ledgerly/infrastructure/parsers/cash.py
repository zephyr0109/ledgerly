import pandas as pd

def preprocess_cash_data(df: pd.DataFrame) -> pd.DataFrame:
    """현금 지출 데이터프레임을 전처리합니다."""
    df = df.copy()
    df["이용일"] = pd.to_datetime(df["이용일"], format="%Y-%m-%d")
    text_cols = ["사용처", "결제수단", "결제제공자", "memo"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    df["금액"] = pd.to_numeric(df["금액"], errors="coerce").fillna(0).astype(int)
    return df

def map_cash_df_to_expenditure(df: pd.DataFrame) -> pd.DataFrame:
    """전처리된 현금 데이터프레임을 지출 공통 포맷으로 매핑합니다."""
    mapped_df = pd.DataFrame()
    mapped_df["used_at"] = df["이용일"]
    mapped_df["merchant_name"] = df["사용처"]
    mapped_df["amount"] = df["금액"]
    mapped_df["payment_type"] = df["결제수단"]
    mapped_df["payment_provider"] = df["결제제공자"]
    mapped_df["memo"] = df["memo"]
    mapped_df["category"] = "unknown"
    mapped_df["installment_type"] = "single"
    mapped_df["remaining_amount"] = 0
    mapped_df["source_uid"] = (
        mapped_df["payment_type"] + "_" + mapped_df["payment_provider"] + "_" +
        mapped_df["used_at"].dt.strftime("%Y%m%d") + "_" + mapped_df["merchant_name"] + "_" + mapped_df["memo"]
    )
    return mapped_df
