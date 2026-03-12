CREATE TABLE income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    income_date TEXT NOT NULL,        -- YYYY-MM-DD
    amount INTEGER NOT NULL,           -- 금액 (원 단위)
    income_type TEXT NOT NULL,         -- 월급, 배당 등
    memo TEXT,                         -- 비고

    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);