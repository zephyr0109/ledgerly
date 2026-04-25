import pandas as pd
import numpy as np
from ledgerly.expenditure.config import kbcard_config

def preprocess_kbcard_data(df: pd.DataFrame) -> pd.DataFrame:
    """국민카드 엑셀 데이터프레임을 가계부 지출 데이터프레임으로 전처리합니다.
    기존 양식과 2026.03 개편 양식을 모두 지원합니다.
    """
    # 양식 판별: 컬럼명이 숫자인 경우(header=None으로 읽은 경우) 개편 양식으로 간주
    is_new_format = isinstance(df.columns[0], int) or df.columns.dtype == "int64"

    if is_new_format:
        # 개편 양식 처리 (데이터는 3번 인덱스부터)
        data_df = df.iloc[3:].copy()
        
        # 컬럼명 설정 (계획서 기준 14개 컬럼 예상)
        # 0: dummy, 1: 이용일자, 2: 이용카드, 3: 구분, 4: 이용하신 가맹점, 5: dummy, 6: 이용금액 ...
        column_names = [
            "dummy_0", "이용일자", "이용카드", "구분", "이용하신 가맹점", "dummy_5",
            "이용금액", "할부개월", "회차", "원금", "수수료_이자", "회차2", "원금2", "적립예정포인트"
        ]
        # 실제 데이터프레임 컬럼 수에 맞춰 슬라이싱 (14개보다 적을 경우 대비)
        data_df.columns = column_names[:len(data_df.columns)]
        
        # 데이터 정제: \xa0(non-breaking space) 제거 및 앞뒤 공백 제거
        for col in ["이용일자", "이용하신 가맹점", "이용금액"]:
            if col in data_df.columns:
                data_df[col] = data_df[col].astype(str).str.replace("\xa0", "", regex=False).str.strip()
        
        # 빈 값(문자열 'nan' 포함)을 실제 NaN으로 변경
        data_df = data_df.replace(["", "nan", "None"], np.nan)
        
        # 이용일자가 없는 행 제거
        data_df = data_df.dropna(subset=["이용일자"])
        
        # 날짜 형식 변환 (26.03.01 -> 2026-03-01)
        def convert_date(x):
            if pd.isna(x): return x
            x = str(x)
            if len(x.split(".")[0]) == 2:
                x = "20" + x
            return x

        data_df["이용일자"] = data_df["이용일자"].apply(convert_date)
        data_df["이용일자"] = pd.to_datetime(data_df["이용일자"], format="%Y.%m.%d", errors="coerce")
        
        # 날짜 변환 실패한 행 제거
        data_df = data_df.dropna(subset=["이용일자"])
        
        # 가맹점명 정제 및 소계 행 제거
        if "이용하신 가맹점" in data_df.columns:
            data_df = data_df[~data_df["이용하신 가맹점"].astype(str).str.contains("소계", na=False)]

        # 금액 변환: '원금' + '수수료_이자' (이번달 결제액) 사용
        # 할부의 경우 전체 금액이 아닌 해당 월 실결제액을 기록하기 위함
        if "원금" in data_df.columns and "수수료_이자" in data_df.columns:
            def calculate_kb_amount(row):
                p = str(row["원금"]).replace(",", "").replace("\xa0", "")
                f = str(row["수수료_이자"]).replace(",", "").replace("\xa0", "")
                try:
                    # 빈 문자열이나 NaN 처리
                    p_val = int(float(p)) if p and p != "nan" else 0
                    f_val = int(float(f)) if f and f != "nan" else 0
                    return p_val + f_val
                except:
                    return 0
            
            data_df["실제결제금액"] = data_df.apply(calculate_kb_amount, axis=1)
            # 기존 이용금액 컬럼을 실제 결제금액으로 교체 (또는 매핑에서 사용)
            data_df["이용금액_원본"] = data_df["이용금액"] 
            data_df["이용금액"] = data_df["실제결제금액"]

        # 할부 정보 및 메모 생성
        def generate_kb_memo(row):
            period = str(row["할부개월"]).strip() if "할부개월" in data_df.columns else ""
            turn = str(row["회차"]).strip() if "회차" in data_df.columns else ""
            total_amt = str(row["이용금액_원본"]).strip() if "이용금액_원본" in data_df.columns else ""
            
            if period and period != "nan" and period.isdigit() and int(period) > 1:
                return f"[할부 {turn}/{period}회차] 총 {total_amt}원"
            return None
            
        data_df["비고"] = data_df.apply(generate_kb_memo, axis=1)
        
        return data_df

    else:
        # 기존 양식 처리
        preprocessed_df = df.copy()
        preprocessed_df.columns = preprocessed_df.columns.str.replace("\n", "", regex=False)

        preprocessed_df["이용일"] = pd.to_datetime(preprocessed_df["이용일"], errors="coerce")
        if "이용시간" in preprocessed_df.columns:
            preprocessed_df["이용시간"] = preprocessed_df["이용시간"].astype("string") + ":00"

        text_cols = ["이용고객명", "이용카드명", "이용하신곳", "결제방법", "상태", "가맹점정보"]
        for col in text_cols:
            if col in preprocessed_df.columns:
                preprocessed_df[col] = preprocessed_df[col].astype("string")

        amount_cols = ["국내이용금액(원)", "해외이용금액($)", "할인금액", "적립(예상)포인트리"]
        for col in amount_cols:
            if col in preprocessed_df.columns:
                preprocessed_df[col] = pd.to_numeric(preprocessed_df[col], errors="coerce").fillna(0).astype("int64")

        return preprocessed_df

def map_kb_card_df_to_expenditure(df: pd.DataFrame, statement_date: str = None) -> pd.DataFrame:
    """국민카드 엑셀 데이터프레임을 가계부 지출 데이터프레임으로 매핑합니다.
    statement_date가 주어지면, 거래일자가 해당 월 이전인 경우 정산월 1일로 조정합니다.
    """
    mapped_df = pd.DataFrame()
    
    # 개편 양식 여부 확인
    is_new_format = "이용일자" in df.columns
    
    if is_new_format:
        # 기본 거래일 설정
        used_dates = pd.to_datetime(df["이용일자"])
        
        # 정산월 기준 날짜 조정 로직
        if statement_date:
            st_date = pd.to_datetime(statement_date)
            def adjust_date(d):
                if d.year < st_date.year or (d.year == st_date.year and d.month < st_date.month):
                    return st_date.replace(day=1).date()
                return d.date()
            mapped_df["used_at"] = used_dates.apply(adjust_date)
        else:
            mapped_df["used_at"] = used_dates.dt.date
            
        mapped_df["merchant_name"] = df["이용하신 가맹점"].astype("string")
        
        # 할부 판정 로직 강화 (숫자 타입 변환 후 체크)
        def get_kb_installment_type(row):
            try:
                period_val = pd.to_numeric(row.get("할부개월"), errors='coerce')
                if not pd.isna(period_val) and int(period_val) > 1:
                    return "installment"
            except:
                pass
            return "single"

        mapped_df["installment_type"] = df.apply(get_kb_installment_type, axis=1)
        mapped_df["amount"] = df["이용금액"]

        # 승인번호가 없으므로 조합하여 생성 (동일 조건 중복 방지를 위해 그룹 내 순번 사용)
        temp_df = mapped_df.copy()
        temp_df["group_seq"] = temp_df.groupby(["used_at", "merchant_name", "amount"]).cumcount() + 1
        
        mapped_df["source_uid"] = (
            kbcard_config["card_company"] + "_" +
            pd.to_datetime(temp_df["used_at"]).dt.strftime("%Y%m%d") + "_" +
            temp_df["merchant_name"].str.replace(" ", "", regex=False).str.replace(r"[^\w]", "", regex=True) + "_" + 
            temp_df["amount"].astype(str) + "_" +
            temp_df["group_seq"].astype(str)
        )
        mapped_df["memo"] = df["비고"] if "비고" in df.columns else None
    else:
        mapped_df["used_at"] = df["이용일"].dt.date
        mapped_df["merchant_name"] = df["이용하신곳"].astype("string")
        mapped_df["installment_type"] = df["결제방법"].map(
            lambda x : "single" if x == "일시불" else "installment"
        )
        
        # 금액 계산
        domestic = pd.to_numeric(df["국내이용금액(원)"], errors="coerce").fillna(0)
        foreign = pd.to_numeric(df["해외이용금액($)"], errors="coerce").fillna(0)
        
        if "상태" in df.columns:
            domestic = np.where(df["상태"] == "승인취소", domestic * -1, domestic)
            foreign = np.where(df["상태"] == "승인취소", foreign * -1, foreign)

        mapped_df["amount"] = (
            np.where(domestic != 0, domestic, foreign * kbcard_config["exchange_rate_usd_to_krw"])
        ).round().astype("int64")
        
        mapped_df["source_uid"] = (
            kbcard_config["payment_type"] + "_" +
            kbcard_config["card_company"] + "_" +
            df["승인번호"].astype("string")
        )
        mapped_df["memo"] = None

    mapped_df["payment_type"] = kbcard_config["payment_type"]
    mapped_df["payment_provider"] = kbcard_config["card_company"]
    mapped_df["remaining_amount"] = 0
    mapped_df["category"] = "unknown"

    return mapped_df
