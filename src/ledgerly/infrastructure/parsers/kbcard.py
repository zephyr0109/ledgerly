import pandas as pd
import numpy as np
from ledgerly.infrastructure.config import kbcard_config

def preprocess_kbcard_data(df: pd.DataFrame) -> pd.DataFrame:
    """국민카드 엑셀 데이터프레임을 가계부 지출 데이터프레임으로 전처리합니다."""
    is_new_format = isinstance(df.columns[0], int) or df.columns.dtype == "int64"

    if is_new_format:
        data_df = df.iloc[3:].copy()
        column_names = [
            "dummy_0", "이용일자", "이용카드", "구분", "이용하신 가맹점", "dummy_5",
            "이용금액", "할부개월", "회차", "원금", "수수료_이자", "회차2", "원금2", "적립예정포인트"
        ]
        data_df.columns = column_names[:len(data_df.columns)]
        
        for col in ["이용일자", "이용하신 가맹점", "이용금액"]:
            if col in data_df.columns:
                data_df[col] = data_df[col].astype(str).str.replace("\xa0", "", regex=False).str.strip()
        
        data_df = data_df.replace(["", "nan", "None"], np.nan)
        data_df = data_df.dropna(subset=["이용일자"])
        
        def convert_date(x):
            if pd.isna(x): return x
            x = str(x)
            if len(x.split(".")[0]) == 2:
                x = "20" + x
            return x

        data_df["이용일자"] = data_df["이용일자"].apply(convert_date)
        data_df["이용일자"] = pd.to_datetime(data_df["이용일자"], format="%Y.%m.%d", errors="coerce")
        data_df = data_df.dropna(subset=["이용일자"])
        
        if "이용하신 가맹점" in data_df.columns:
            data_df = data_df[~data_df["이용하신 가맹점"].astype(str).str.contains("소계", na=False)]

        if "원금" in data_df.columns and "수수료_이자" in data_df.columns:
            def calculate_kb_amount(row):
                p = str(row["원금"]).replace(",", "").replace("\xa0", "")
                f = str(row["수수료_이자"]).replace(",", "").replace("\xa0", "")
                try:
                    p_val = int(float(p)) if p and p != "nan" else 0
                    f_val = int(float(f)) if f and f != "nan" else 0
                    return p_val + f_val
                except:
                    return 0
            
            data_df["실제결제금액"] = data_df.apply(calculate_kb_amount, axis=1)
            data_df["이용금액_원본"] = data_df["이용금액"] 
            data_df["이용금액"] = data_df["실제결제금액"]

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
        preprocessed_df = df.copy()
        preprocessed_df.columns = preprocessed_df.columns.str.replace("\n", "", regex=False)
        preprocessed_df["이용일"] = pd.to_datetime(preprocessed_df["이용일"], errors="coerce")
        if "이용시간" in preprocessed_df.columns:
            preprocessed_df["이용시간"] = preprocessed_df["이용시간"].astype("string") + ":00"
        return preprocessed_df

def map_kb_card_df_to_expenditure(df: pd.DataFrame, statement_date: str = None) -> pd.DataFrame:
    """국민카드 데이터프레임을 지출 데이터로 매핑합니다."""
    mapped_df = pd.DataFrame()
    is_new_format = "이용일자" in df.columns
    
    if is_new_format:
        used_dates = pd.to_datetime(df["이용일자"])
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
        
        def get_kb_installment_type(row):
            try:
                period_val = pd.to_numeric(row.get("할부개월"), errors='coerce')
                if not pd.isna(period_val) and int(period_val) > 1:
                    return "installment"
            except: pass
            return "single"

        mapped_df["installment_type"] = df.apply(get_kb_installment_type, axis=1)
        mapped_df["amount"] = df["이용금액"]

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
        # 기존 양식 로직 (간소화)
        mapped_df["used_at"] = df["이용일"].dt.date
        mapped_df["merchant_name"] = df["이용하신곳"].astype("string")
        mapped_df["installment_type"] = df["결제방법"].map(lambda x : "single" if x == "일시불" else "installment")
        mapped_df["amount"] = df["국내이용금액(원)"].round().astype("int64")
        mapped_df["source_uid"] = kbcard_config["card_company"] + "_" + df["승인번호"].astype("string")
        mapped_df["memo"] = None

    mapped_df["payment_type"] = kbcard_config["payment_type"]
    mapped_df["payment_provider"] = kbcard_config["card_company"]
    mapped_df["remaining_amount"] = 0
    mapped_df["category"] = "unknown"

    return mapped_df
