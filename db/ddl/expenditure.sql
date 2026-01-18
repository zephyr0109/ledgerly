CREATE TABLE expenditure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- 사용일
    used_at DATE NOT NULL,

    -- 결제 수단
    payment_type TEXT NOT NULL,

    -- 카드사 (카드 결제일 때만)
    card_company TEXT,

    -- 사용처
    merchant_name TEXT NOT NULL,

    -- 결제 방식
    installment_type TEXT NOT NULL
        CHECK (installment_type IN ('single', 'installment')),

    -- 총 결제 금액
    amount INTEGER NOT NULL CHECK (amount >= 0),

    -- 할부 잔액 (일시불이면 0)
    remaining_amount INTEGER NOT NULL DEFAULT 0 CHECK (remaining_amount >= 0),

    -- 분류
    category TEXT NOT NULL,

    -- 메모 (선택)
    memo TEXT,

    -- 원본 식별자 (중복 방지용)
    source_uid TEXT UNIQUE,

    -- 생성 시각
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);