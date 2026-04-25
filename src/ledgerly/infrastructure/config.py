from pathlib import Path
from ledgerly.utils import find_project_root

PROJECT_ROOT = find_project_root()
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# 카드사 및 결제 수단별 설정
kbcard_config = {
    "exchange_rate_usd_to_krw": 1450,
    "payment_type": "card",
    "card_company": "kb",
}

shinhan_config = {
    "payment_type": "card",
    "card_company": "shinhan",
}

cash_config = {
    "payment_type": "cash",
    "payment_provider": "cash",
}

# 파일 경로 관련 설정
kbcard_file_config = {
    "data_dir": RAW_DATA_DIR,
    "project_root": PROJECT_ROOT
}

shinhan_file_config = {
    "data_dir": RAW_DATA_DIR,
    "project_root": PROJECT_ROOT
}

cash_file_config = {
    "data_dir": RAW_DATA_DIR,
    "project_root": PROJECT_ROOT
}
