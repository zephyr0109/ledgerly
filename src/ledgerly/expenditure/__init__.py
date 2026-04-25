from ledgerly.usecases.expenditure import ExpenditureUseCase
from ledgerly.infrastructure.parsers.kbcard import preprocess_kbcard_data, map_kb_card_df_to_expenditure
from ledgerly.infrastructure.parsers.shinhan import preprocess_shinhan_data, map_shinhan_card_df_to_expenditure, load_shinhan_html_file
from ledgerly.infrastructure.parsers.cash import preprocess_cash_data, map_cash_df_to_expenditure
from ledgerly.infrastructure.category_mapper import map_category
from ledgerly.infrastructure.config import kbcard_file_config, shinhan_file_config, cash_file_config

_usecase = ExpenditureUseCase()

def insert_expenditure_data(df):
    return _usecase.import_from_dataframe(df)

def fetch_expenditure_data():
    return _usecase.get_all_expenditures()

__all__ = [
    "insert_expenditure_data",
    "fetch_expenditure_data",
    "preprocess_kbcard_data",
    "map_kb_card_df_to_expenditure",
    "preprocess_shinhan_data",
    "map_shinhan_card_df_to_expenditure",
    "load_shinhan_html_file",
    "preprocess_cash_data",
    "map_cash_df_to_expenditure",
    "map_category",
    "kbcard_file_config",
    "shinhan_file_config",
    "cash_file_config",
]
