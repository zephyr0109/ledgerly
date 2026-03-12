import pandas as pd

from ledgerly.expenditure.config import kbcard_config

def preprocess_kbcard_data(df: pd.DataFrame) -> pd.DataFrame:
    """국민카드 엑셀 데이터프레임을 가계부 지출 데이터프레임으로 전처리합니다."""
    preprocessed_df = df.copy()
    # 헤더 줄바꿈 지우기. 국민은행은 헤더에 보기좋으라고 줄바꿈을 해둠
    preprocessed_df.columns = preprocessed_df.columns.str.replace("\n", "", regex=False)

    # 날짜 형식 변환
    # 날짜 컬럼을 datetime 타입으로 변환
    preprocessed_df["이용일"] = pd.to_datetime(preprocessed_df["이용일"], errors="coerce")
    preprocessed_df["결제예정일"] = pd.to_datetime(preprocessed_df["결제예정일"], errors="coerce")
    preprocessed_df["이용시간"] = preprocessed_df["이용시간"].astype("string") + ":00"

    # 텍스트 컬럼 변경
    text_cols = [
    "이용고객명",
    "이용카드명",
    "이용하신곳",
    "결제방법",
    "상태",
    "가맹점정보",
    ]

    for col in text_cols:
        preprocessed_df[col] = preprocessed_df[col].astype("string")

    # 금액 컬럼 변경
    amount_cols = [
        "국내이용금액(원)",
        "해외이용금액($)",
        "할인금액",
        "적립(예상)포인트리",
    ]
    preprocessed_df[amount_cols] = preprocessed_df[amount_cols].fillna(0).astype("int64")

    return preprocessed_df



def map_kb_card_df_to_expenditure(df: pd.DataFrame) -> pd.DataFrame:
    """국민카드 엑셀 데이터프레임을 가계부 지출 데이터프레임으로 매핑합니다."""
    mapped_df = pd.DataFrame()
    #사용일(Date)
    mapped_df["used_at"] = df["이용일"].dt.date

    #결제 수단 / 카드사(고정값 처리)
    mapped_df["payment_type"] = kbcard_config["payment_type"]
    mapped_df["payment_provider"] = kbcard_config["card_company"]

    #사용처
    mapped_df["merchant_name"] = df["이용하신곳"].astype("string")

    #결제 방식
    mapped_df["installment_type"] = df["결제방법"].map(
        lambda x : "single" if x == "일시불" else "installment"
    )


    #금액 계산
     # 금액 계산 (국내 우선, 해외는 환율 적용)
    df.loc[df["상태"] == "승인취소", "국내이용금액(원)"] *= -1
    df.loc[df["상태"] == "승인취소", "해외이용금액($)"] *= -1


    domestic = pd.to_numeric(
        df["국내이용금액(원)"],
        errors="coerce"
    ).fillna(0)

    foreign = pd.to_numeric(
        df["해외이용금액($)"],
        errors="coerce"
    ).fillna(0)

    mapped_df["amount"] = (
        domestic.where(domestic > 0, foreign * kbcard_config["exchange_rate_usd_to_krw"])
        .round()
        .astype("int64")
    )

     # 할부 잔액
    mapped_df["remaining_amount"] = 0

    # 분류 (임시)
    mapped_df["category"] = "unknown"

    # 메모
    mapped_df["memo"] = None

    # 원본 식별자
    mapped_df["source_uid"] = (
        kbcard_config["payment_type"]
        + "_"
        + kbcard_config["card_company"]
        + "_"
        + df["승인번호"].astype("string")
    )
    return mapped_df