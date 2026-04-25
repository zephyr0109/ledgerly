
import pandas as pd
import numpy as np
import re

def test_shinhan_final_check(file_path):
    print(f"Final check for {file_path}...")
    tables = pd.read_html(file_path, encoding='utf-8')
    df = tables[9] # 메인 데이터 테이블
    
    date_pattern = re.compile(r'^\d{4}\.\d{2}\.\d{2}$')
    mask = df.iloc[:, 0].astype(str).apply(lambda x: bool(date_pattern.match(x)))
    data_df = df[mask].copy()
    
    print(f"Found {len(data_df)} usage records.")
    
    # 가독성을 위해 컬럼명을 숫자로 변경
    data_df.columns = [f"Col_{i}" for i in range(len(data_df.columns))]
    
    # 상위 10개 레코드 출력 (금액 확인 위주)
    print("\n--- Usage Data Samples ---")
    for i in range(min(10, len(data_df))):
        row = data_df.iloc[i]
        print(f"Date: {row['Col_0']} | Merchant Index 1: {row['Col_1'][:20]} | Amount Col 2: {row['Col_2']} | Amount Col 6: {row['Col_6']}")

if __name__ == "__main__":
    test_shinhan_final_check('data/raw/2603/shinhancard_2603.xls')
