import pandas as pd
from ledgerly.infrastructure.parsers.kbcard import preprocess_kbcard_data, map_kb_card_df_to_expenditure
from ledgerly.infrastructure.parsers.cash import preprocess_cash_data, map_cash_df_to_expenditure

def test_kbcard_parser():
    # KB카드 개편 양식 모사 (header=None)
    data = [
        ["dummy", "dummy", "dummy", "dummy"],
        ["dummy", "dummy", "dummy", "dummy"],
        ["dummy", "dummy", "dummy", "dummy"],
        [None, "26.03.01", "card1", "일시불", "Store A", "", "10000", "", "", "10000", "0", "", "", ""]
    ]
    df = pd.DataFrame(data)
    pre_df = preprocess_kbcard_data(df)
    assert len(pre_df) == 1
    
    mapped_df = map_kb_card_df_to_expenditure(pre_df)
    assert mapped_df.iloc[0]["merchant_name"] == "Store A"
    assert mapped_df.iloc[0]["amount"] == 10000

def test_cash_parser():
    data = {
        "이용일": ["2026-04-25"],
        "사용처": ["Market"],
        "금액": [5000],
        "결제수단": ["Cash"],
        "결제제공자": ["KB"],
        "memo": ["test"]
    }
    df = pd.DataFrame(data)
    pre_df = preprocess_cash_data(df)
    mapped_df = map_cash_df_to_expenditure(pre_df)
    assert mapped_df.iloc[0]["amount"] == 5000
    assert "Market" in mapped_df.iloc[0]["source_uid"]
