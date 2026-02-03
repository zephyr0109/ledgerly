
import pandas as pd

from ledgerly.expenditure.config import shinhan_config


def preprocess_shinhan_data(df: pd.DataFrame) -> pd.DataFrame:
    """신한카드 엑셀 데이터프레임을 가계부 지출 데이터프레임으로 전처리합니다."""
    preprocessed_df = df.copy()

    preprocessed_df["승인번호"]= (preprocessed_df["승인번호"].dropna()
    .astype("int64")
    .astype("str"))

    # 날짜 형식 변환
    preprocessed_df["거래일"] = pd.to_datetime(preprocessed_df["거래일"], errors="coerce")

    # 텍스트 컬럼 변경
    text_cols = [
        "가맹점명",
        "이용구분",
        "매입구분"
    ]

    for col in text_cols:
        preprocessed_df[col] = preprocessed_df[col].astype("string")

    # 금액 컬럼 변경
    preprocessed_df["금액"] = pd.to_numeric(preprocessed_df["금액"], errors="coerce").fillna(0).astype("int64")

    # 맨 마지막 요약 행 제거
    preprocessed_df = preprocessed_df.iloc[:-1]

    return preprocessed_df

def map_shinhan_card_df_to_expenditure(df: pd.DataFrame) -> pd.DataFrame:
    """신한카드 엑셀 데이터프레임을 가계부 지출 데이터프레임으로 매핑합니다."""
    mapped_df = pd.DataFrame()
    mapped_df["used_at"] = df["거래일"]
    mapped_df["payment_type"] = shinhan_config["payment_type"]
    mapped_df["payment_provider"] = shinhan_config["card_company"]
    mapped_df["merchant_name"] = df["가맹점명"]

    mapped_df["installment_type"] = df["이용구분"].map(
        lambda x: "single" if x == "일시불" else "installment"
    )

    mapped_df["amount"] = df["금액"]
    mapped_df["remaining_amount"] = 0
    mapped_df["category"] = "unknown"
    mapped_df["memo"] = None
    mapped_df["source_uid"] = (
        shinhan_config["payment_type"]
        + "_"
        + shinhan_config["card_company"]
        + "_" + df["승인번호"]
    )

    return mapped_df
