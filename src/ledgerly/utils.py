# 지출 매핑 파일을 불러옵니다.
from pathlib import Path

def find_project_root(
    start_path: Path | None = None,
    markers=("pyproject.toml", ".git")
) -> Path:
    """
    start_path부터 상위 디렉토리를 탐색하며
    markers 중 하나가 존재하는 디렉토리를 프로젝트 루트로 반환
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    for parent in [current] + list(current.parents):
        if any((parent / marker).exists() for marker in markers):
            return parent

    raise RuntimeError("프로젝트 루트를 찾을 수 없습니다.")
