import sqlite3
from pathlib import Path
from contextlib import contextmanager
from ledgerly.utils import find_project_root

class SqliteDatabase:
    """Sqlite DB 연결 및 기본 연산을 담당하는 인프라 클래스입니다."""
    
    def __init__(self, db_path: Path = None):
        if db_path is None:
            self.db_path = find_project_root() / 'data' / 'db' / 'ledgerly.db'
        else:
            self.db_path = db_path
            
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 컬럼명으로 접근 가능하게 설정
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

# 싱글톤 인스턴스 또는 기본 DB 객체
default_db = SqliteDatabase()
