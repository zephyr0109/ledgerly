import pandas as pd
import numpy as np
import re
from lxml import html
from ledgerly.infrastructure.config import shinhan_config

def load_shinhan_html_file(file_path: str) -> pd.DataFrame:
    """신한카드 HTML(XLS) 파일에서 데이터를 추출합니다."""
    try:
        with open(file_path, "rb") as f:
            content = f.read().decode("utf-8", errors="ignore")
        tree = html.fromstring(content)
        target_tables = tree.xpath('//table[caption[contains(text(), "이용일자별 카드사용내역")]]')
        if not target_tables:
            return pd.DataFrame()
        table_html = html.tostring(target_tables[0], encoding="unicode")
        df_list = pd.read_html(table_html)
        return df_list[0] if df_list else pd.DataFrame()
    except Exception as e:
        print(f"HTML 파싱 오류: {e}")
        return pd.DataFrame()

def preprocess_shinhan_data(df: pd.DataFrame) -> pd.DataFrame:
    """신한카드 데이터를 전처리합니다."""
    date_pattern = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')
    mask = pd.Series(False, index=df.index)
    date_col_name = None
    for col in df.columns:
        val_sample = df[col].astype(str)
        temp_mask = val_sample.apply(lambda x: bool(date_pattern.match(x)))
        if temp_mask.any():
            mask = temp_mask
            date_col_name = col
            break

    if date_col_name is not None:
        data_df = df[mask].copy()
        current_cols = df.columns.tolist()
        date_idx = current_cols.index(date_col_name)
        data_df.columns = range(data_df.shape[1])
        data_df["거래일"] = pd.to_datetime(data_df[date_idx], errors="coerce")
        merchant_col = date_idx + 2
        data_df["가맹점명"] = data_df[merchant_col].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip() if merchant_col < data_df.shape[1] else "알수없음"
        principal_col = date_idx + 6
        fee_col = date_idx + 7
        def calculate_amount(row):
            p = str(row[principal_col]).replace(",", "").replace("\xa0", "") if principal_col < data_df.shape[1] else "0"
            f = str(row[fee_col]).replace(",", "").replace("\xa0", "") if fee_col < data_df.shape[1] else "0"
            try: return int(float(p)) + int(float(f))
            except: return 0
        data_df["금액"] = data_df.apply(calculate_amount, axis=1)
        total_amt_col = date_idx + 3
        period_col = date_idx + 4
        turn_col = date_idx + 5
        def generate_memo_and_type(row):
            try:
                period_val = pd.to_numeric(row[period_col], errors='coerce')
                turn_val = pd.to_numeric(row[turn_col], errors='coerce')
                if not pd.isna(period_val) and int(period_val) > 1:
                    period = str(int(period_val))
                    turn = str(int(turn_val)) if not pd.isna(turn_val) else "?"
                    total_amt = str(row[total_amt_col]).strip()
                    return "installment", f"[할부 {turn}/{period}회차] 총 {total_amt}원"
            except: pass
            return "single", None
        res = data_df.apply(generate_memo_and_type, axis=1)
        data_df["이용구분"] = res.apply(lambda x: x[0])
        data_df["비고"] = res.apply(lambda x: x[1])
        data_df["is_new_format"] = True
        return data_df
    else:
        # 기존 엑셀 양식 생략/간소화
        return df

def map_shinhan_card_df_to_expenditure(df: pd.DataFrame, statement_date: str = None) -> pd.DataFrame:
    """신한카드 데이터를 지출 데이터로 매핑합니다."""
    mapped_df = pd.DataFrame()
    is_new_format = "is_new_format" in df.columns
    used_dates = pd.to_datetime(df["거래일"])
    if statement_date:
        st_date = pd.to_datetime(statement_date)
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
    mapped_df["installment_type"] = df["이용구분"].map(lambda x: "installment" if "installment" in str(x) or "할부" in str(x) else "single")
    mapped_df["amount"] = df["금액"]
    mapped_df["remaining_amount"] = 0
    mapped_df["category"] = "unknown"
    mapped_df["memo"] = df["비고"] if "비고" in df.columns else None
    
    temp_df = mapped_df.copy()
    temp_df["group_seq"] = temp_df.groupby(["used_at", "merchant_name", "amount"]).cumcount() + 1
    mapped_df["source_uid"] = ("shinhan_" + pd.to_datetime(temp_df["used_at"]).dt.strftime("%Y%m%d") + "_" +
        temp_df["merchant_name"].str.replace(" ", "", regex=False).str.replace(r"[^\w]", "", regex=True) + "_" + 
        temp_df["amount"].astype(str) + "_" + temp_df["group_seq"].astype(str))
    return mapped_df
