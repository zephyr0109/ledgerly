# Ledgerly UI 고도화 및 아키텍처 재구성 계획 (v2)

## 1. 아키텍처 원칙: 클린 아키텍처와 실험실의 결합
- **Domain/UseCases:** 핵심 계산 로직 및 DB 규칙 (노트북, UI, CLI 공동 사용)
- **Infrastructure:** SQLite DB, CSV 처리기
- **Interfaces:**
    - **Notebooks (Lab):** 새로운 데이터 분석 모델이나 카테고리 분류 로직 실험
    - **Web (Service):** FastAPI + Streamlit 기반의 홈 네트워크 서비스
    - **CLI (Admin):** 배치 작업 및 시스템 관리

## 2. 사용자 시나리오
- **사용자 (Admin):** 
    - 노트북에서 새로운 소비 패턴 분석 코드 작성 및 실험.
    - 검증된 코드를 `usecases`로 이관.
    - UI 혹은 CLI를 통해 대량 CSV 임포트 및 누락된 데이터 수동 입력.
- **가족 (Viewer/Guest):**
    - 홈 네트워크 브라우저를 통해 `asset_report` 및 지출 현황 조회 (Read-only 모드).

## 3. 상세 구현 단계

### Phase 1: 도메인 로직의 중앙 집중화 (Refactoring) - 진행 중
- [x] 지출(Expenditure) 도메인 모델 (`domain/expenditure.py`) 정의.
- [x] 지출 유스케이스 레이어 (`app/usecases/expenditure.py`) 구축.
- [ ] 자산(Asset), 부채(Debt) 로직의 도메인/유스케이스 추출.
- [ ] 노트북(`ipynb`)에서 이 `usecases`를 `import`하여 사용하도록 구조 변경 (실험실의 도구화).

### Phase 2: 웹 인터페이스 구축 (FastAPI + Streamlit)
- [ ] **Backend (API):** 데이터 조회 및 수동 입력을 위한 REST API (FastAPI) 구축.
- [ ] **Frontend (UI):** 
    - 조회용: 노트북의 시각화 결과물을 대시보드화 (Streamlit).
    - 입력용: 직접 DB에 기록할 수 있는 폼(Form) 페이지 구현.

### Phase 3: 통합 및 배포
- [ ] 단일 실행 스크립트 제공: `uv run ledgerly web` 명령으로 서버 구동.
- [ ] 홈 네트워크 내 고정 IP 혹은 호스트네임 접근 설정 가이드 마련.
