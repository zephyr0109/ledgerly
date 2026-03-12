CREATE TABLE debt_account (
    debt_id TEXT PRIMARY KEY,        -- 사람이 지정하는 고유키
    owner TEXT NOT NULL,             -- ME / WIFE / JOINT
    debt_name TEXT NOT NULL,         -- 학자금, 주담대 등
    initial_principal INTEGER NOT NULL CHECK (initial_principal > 0),
    repayment_type TEXT,             -- 원리금균등, 만기일시 등
    maturity_date TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')), -- 생성일
    updated_at TEXT NOT NULL DEFAULT (datetime('now')), -- 수정일
    memo TEXT -- 기타 메모 사항
);

CREATE TABLE debt_snapshot (
    debt_id TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,         -- YYYY-MM-DD

    principal_amount INTEGER NOT NULL,   -- 원금 잔액
    interest_rate REAL NOT NULL,         -- 이자율 (%)
    accrued_interest INTEGER,            -- 누적 이자 (선택)

    PRIMARY KEY (debt_id, snapshot_date),
    FOREIGN KEY (debt_id) REFERENCES debt_account(debt_id)
);