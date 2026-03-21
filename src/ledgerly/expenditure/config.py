
from pathlib import Path

from ledgerly.utils import find_project_root;


# KB국민카드 관련 설정
kbcard_config = {
    "exchange_rate_usd_to_krw": 1450,
    "payment_type": "card",
    "card_company": "kb",
}

shinhan_config ={
    "payment_type": "card",
    "card_company": "shinhan",
}

cash_config = {
    "payment_type": "cash",
    "payment_provider": "cash", # 기본값
}

# 데이터 파일 경로 설정
kbcard_file_config = {
    "data_dir": find_project_root(Path.cwd()) / "data" / "raw",
    "project_root": find_project_root(Path.cwd())
}

shinhan_file_config = {
    "data_dir": find_project_root(Path.cwd()) / "data" / "raw",
    "project_root": find_project_root(Path.cwd())
}

cash_file_config = {
    "data_dir": find_project_root(Path.cwd()) / "data" / "raw",
    "project_root": find_project_root(Path.cwd())
}