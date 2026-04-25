
import pandas as pd
import re

def debug():
    tables = pd.read_html('data/raw/2603/shinhancard_2603.xls', encoding='utf-8')
    t9 = tables[9]
    mask = t9.iloc[:, 0].astype(str).apply(lambda x: bool(re.match(r'^\d{4}\.\d{2}\.\d{2}$', x)))
    data = t9[mask]
    
    with open('shinhan_debug.txt', 'w', encoding='utf-8') as f:
        for i, row in data.iterrows():
            clean_list = [str(x).replace('\n', ' ').strip() for x in row.tolist()]
            f.write(f"Row {i}: {clean_list}\n")
    
    print("Debug info written to shinhan_debug.txt")

if __name__ == "__main__":
    debug()
