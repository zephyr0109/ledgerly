import pandas as pd
import numpy as np
import re
from lxml import html
from ledgerly.expenditure.config import shinhan_config

def load_shinhan_html_file(file_path: str) -> pd.DataFrame:
    """신한카드 HTML(XLS) 파일에서 '이용일자별 카드사용내역' 테이블만 정확히 추출합니다."""
    try:
        with open(file_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")
        
        tree = html.fromstring(content)
        # 캡션에 '이용일자별 카드사용내역'이 포함된 테이블 검색
        target_tables = tree.xpath('//table[caption[contains(text(), "이용일자별 카드사용내역")]]')
        
        if not target_tables:
            return pd.DataFrame()
            
        # 선택된 테이블만 pandas 데이터프레임으로 변환
        table_html = html.tostring(target_tables[0], encoding="unicode")
        # read_html은 리스트를 반환하므로 첫 번째 요소 선택
        df_list = pd.read_html(table_html)
        return df_list[0] if df_list else pd.DataFrame()
        
    except Exception as e:
        print(f"HTML 파싱 오류: {e}")
        return pd.DataFrame()

def preprocess_shinhan_data(df: pd.DataFrame) -> pd.DataFrame:
    """신한카드 데이터를 가계부 지출 데이터프레임으로 전처리합니다.
    기존 엑셀 양식과 2026.03 개편(HTML 기반) 양식을 모두 지원합니다.
    """
    # 0번 컬럼에서 날짜 패턴(YYYY.MM.DD)인 행 찾기
    date_pattern = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')
    
    # 데이터프레임의 모든 컬럼을 문자열로 변환하여 날짜 패턴 탐색
    mask = pd.Series(False, index=df.index)
    date_col_name = None
    
    for col in df.columns:
        # 멀티인덱스일 경우 첫 번째 요소만 사용하여 체크
        val_sample = df[col].astype(str)
        temp_mask = val_sample.apply(lambda x: bool(date_pattern.match(x)))
        if temp_mask.any():
            mask = temp_mask
            date_col_name = col
            break

    if date_col_name is not None:
        # 개편(HTML) 또는 날짜 기반 양식 처리
        data_df = df[mask].copy()
        
        # 멀티인덱스 또는 복잡한 컬럼명을 숫자로 강제 초기화 (0, 1, 2...)
        current_cols = df.columns.tolist()
        date_idx = current_cols.index(date_col_name)
        data_df.columns = range(data_df.shape[1])
        
        # 날짜 변환
        data_df["거래일"] = pd.to_datetime(data_df[date_idx], errors="coerce")
        
        # 가맹점명 (날짜 기준 2번째 뒤 컬럼)
        merchant_col = date_idx + 2
        if merchant_col < data_df.shape[1]:
            data_df["가맹점명"] = data_df[merchant_col].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
        else:
            data_df["가맹점명"] = "알수없음"
            
        # 금액: '이번달 내실금액' (원금 + 수수료) 사용 (날짜 기준 6, 7번째 뒤 컬럼)
        # 할부의 경우 전체 금액이 아닌 해당 월 결제 금액을 기록하기 위함
        principal_col = date_idx + 6
        fee_col = date_idx + 7
        
        def calculate_amount(row):
            p = str(row[principal_col]).replace(",", "").replace("\xa0", "") if principal_col < data_df.shape[1] else "0"
            f = str(row[fee_col]).replace(",", "").replace("\xa0", "") if fee_col < data_df.shape[1] else "0"
            try:
                return int(float(p)) + int(float(f))
            except:
                return 0
                
        data_df["금액"] = data_df.apply(calculate_amount, axis=1)
        
        # 할부 정보 및 메모 생성 (날짜 기준 3:총액, 4:할부기간, 5:회차)
        total_amt_col = date_idx + 3
        period_col = date_idx + 4
        turn_col = date_idx + 5
        
        def generate_memo_and_type(row):
            try:
                # pandas가 숫자를 float으로 읽을 수 있으므로(3.0 등) to_numeric 사용
                period_val = pd.to_numeric(row[period_col], errors='coerce')
                turn_val = pd.to_numeric(row[turn_col], errors='coerce')
                
                if not pd.isna(period_val) and int(period_val) > 1:
                    period = str(int(period_val))
                    turn = str(int(turn_val)) if not pd.isna(turn_val) else "?"
                    total_amt = str(row[total_amt_col]).strip()
                    memo = f"[할부 {turn}/{period}회차] 총 {total_amt}원"
                    return "installment", memo
            except:
                pass
            return "single", None
            
        res = data_df.apply(generate_memo_and_type, axis=1)
        data_df["이용구분"] = res.apply(lambda x: x[0])
        data_df["비고"] = res.apply(lambda x: x[1])
        
        data_df["is_new_format"] = True
        
        return data_df

    else:
        # 기존 엑셀 양식 처리
        preprocessed_df = df.copy()

        if "승인번호" in preprocessed_df.columns:
            preprocessed_df["승인번호"]= (preprocessed_df["승인번호"].dropna()
            .astype("int64")
            .astype("str"))

        # 날짜 형식 변환
        if "거래일" in preprocessed_df.columns:
            preprocessed_df["거래일"] = pd.to_datetime(preprocessed_df["거래일"], errors="coerce")

        # 텍스트 컬럼 변경
        text_cols = ["가맹점명", "이용구분", "매입구분"]
        for col in text_cols:
            if col in preprocessed_df.columns:
                preprocessed_df[col] = preprocessed_df[col].astype("string")

        # 금액 컬럼 변경
        if "금액" in preprocessed_df.columns:
            preprocessed_df["금액"] = pd.to_numeric(preprocessed_df["금액"], errors="coerce").fillna(0).astype("int64")

        # 맨 마지막 요약 행 제거
        if len(preprocessed_df) > 0:
            preprocessed_df = preprocessed_df.iloc[:-1]

        return preprocessed_df

def map_shinhan_card_df_to_expenditure(df: pd.DataFrame, statement_date: str = None) -> pd.DataFrame:
    """신한카드 데이터프레임을 가계부 지출 데이터프레임으로 매핑합니다.
    statement_date가 주어지면, 거래일자가 해당 월 이전인 경우 정산월 1일로 조정합니다.
    """
    mapped_df = pd.DataFrame()
    
    # 개편 양식 여부 확인
    is_new_format = "is_new_format" in df.columns
    
    # 기본 거래일 설정
    used_dates = pd.to_datetime(df["거래일"])
    
    # 정산월 기준 날짜 조정 로직
    if statement_date:
        st_date = pd.to_datetime(statement_date)
        # 거래일의 연/월이 정산월과 다르면 정산월 1일로 조정 (과거 할부 결제분 등)
        def adjust_date(d):
            if d.year < st_date.year or (d.year == st_date.year and d.month < st_date.month):
                return st_date.replace(day=1).date()
            return d.date()
        
        mapped_df["used_at"] = used_dates.apply(adjust_date)
    else:
        mapped_df["used_at"] = used_dates.dt.date
    mapped_df["payment_type"] = shinhan_config["payment_type"]
    mapped_df["payment_provider"] = shinhan_config["card_company"]
    mapped_df["merchant_name"] = df["가맹점명"].astype("string")

    mapped_df["installment_type"] = df["이용구분"].map(
        lambda x: "installment" if "installment" in str(x) or "할부" in str(x) else "single"
    )

    mapped_df["amount"] = df["금액"]
    mapped_df["remaining_amount"] = 0
    mapped_df["category"] = "unknown"
    mapped_df["memo"] = df["비고"] if "비고" in df.columns else None
    
    if is_new_format:
        # 승인번호가 없으므로 조합하여 생성 (동일 조건 중복 방지를 위해 그룹 내 순번 사용)
        temp_df = mapped_df.copy()
        temp_df["group_seq"] = temp_df.groupby(["used_at", "merchant_name", "amount"]).cumcount() + 1
        
        mapped_df["source_uid"] = (
            "shinhan_" +
            pd.to_datetime(temp_df["used_at"]).dt.strftime("%Y%m%d") + "_" +
            temp_df["merchant_name"].str.replace(" ", "", regex=False).str.replace(r"[^\w]", "", regex=True) + "_" + 
            temp_df["amount"].astype(str) + "_" +
            temp_df["group_seq"].astype(str)
        )
    else:
        mapped_df["source_uid"] = (
            shinhan_config["payment_type"]
            + "_"
            + shinhan_config["card_company"]
            + "_" + df.get("승인번호", df.index.astype(str))
        )

    return mapped_df
