CREATE TABLE asset_account (
    asset_id TEXT PRIMARY KEY,  -- 사람이 지정하는 고유키
    asset_name TEXT NOT NULL,   -- 진영 카뱅 통장, 주택 시세 등
    category TEXT NOT NULL,     -- 자율예금, 현물 등
    owner TEXT NOT NULL,        -- 진영, 준열, 공동
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    memo TEXT
);

CREATE TABLE asset_snapshot (
    asset_id TEXT NOT NULL,
    snapshot_date TEXT NOT NULL,  -- YYYY-MM-DD

    amount INTEGER NOT NULL CHECK (amount >= 0),  -- 평가 금액
    rate REAL,  -- 이율 또는 수익률 (선택)

    PRIMARY KEY (asset_id, snapshot_date),
    FOREIGN KEY (asset_id)
        REFERENCES asset_account(asset_id)
        ON DELETE RESTRICT
);