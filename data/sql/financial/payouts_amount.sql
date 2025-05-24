WITH
currencies AS (                   -- 1. средний курс валюты за день
    SELECT
        crh.currency::text               AS currency,
        to_timestamp(crh.created_at)::date AS exchange_date,
        AVG(crh.usd_ratio)               AS exchange_ratio
    FROM currencies_rates_history crh
    GROUP BY 1,2
),
/* ----------------------------------------------------------------
   2. ежедневная сумма выплат в валюте игрока по каждой таблице
   ---------------------------------------------------------------- */
daily_payouts AS (
    /* ---------- betslips -------------------------------------- */
    SELECT
        date_trunc('day', to_timestamp(b."timestamp"))::date AS payout_date,
        b.currency::text                                     AS currency,
        SUM(b.amount_won)::numeric / 100                     AS payout_amount
    FROM betslips b
    JOIN users u ON u.id = b.user_id AND u.is_fake = FALSE
    WHERE b.status IN ('WIN','LOSE','CASHOUT')
    GROUP BY 1,2

    UNION ALL

    /* ---------- slotegrator_transactions ---------------------- */
    SELECT
        st."timestamp"::date,
        u.currency::text,
        SUM(st.amount)::numeric / 100
    FROM slotegrator_transactions st
    JOIN users u ON u.id = st.user_id AND u.is_fake = FALSE
    WHERE st.type IN ('WIN','JACKPOT')
    GROUP BY 1,2

    UNION ALL

    /* ---------- casino_transaction_only_play ------------------ */
    SELECT
        date_trunc('day', to_timestamp(t.created_at))::date,
        u.currency::text,
        SUM(t.amount)::numeric / 100
    FROM casino_transaction_only_play t
    JOIN users u ON u.id = t.user_id AND u.is_fake = FALSE
    WHERE t.type IN ('WIN','CANCEL')
    GROUP BY 1,2

    UNION ALL

    /* ---------- casino_transaction_claw_buster ---------------- */
    SELECT
        t.created_at::date,
        u.currency::text,
        SUM(t.amount)::numeric / 100
    FROM casino_transaction_claw_buster t
    JOIN users u ON u.id = t.user_id AND u.is_fake = FALSE
    WHERE t.type IN ('WIN','JACKPOT','ROLLBACK')
    GROUP BY 1,2

    UNION ALL

    /* ---------- casino_transaction_inout ---------------------- */
    SELECT
        t.created_at::date,
        u.currency::text,
        SUM(t.amount)::numeric / 100
    FROM casino_transaction_inout t
    JOIN users u ON u.id = t.user_id AND u.is_fake = FALSE
    WHERE t.type IN ('WIN','ROLLBACK')
    GROUP BY 1,2

    UNION ALL

    /* ---------- casino_transaction_nexgenspin ----------------- */
    SELECT
        t.created_at::date,
        u.currency::text,
        SUM(t.amount)::numeric / 100
    FROM casino_transaction_nexgenspin t
    JOIN users u ON u.id = t.user_id AND u.is_fake = FALSE
    WHERE t.type IN ('WIN','ROLLBACK')
    GROUP BY 1,2
),
/* ----------------------------------------------------------------
   3. сводим шесть потоков в один (день-валюта)
   ---------------------------------------------------------------- */
payouts_by_curr AS (
    SELECT
        payout_date,
        currency,
        SUM(payout_amount) AS payout_amount
    FROM daily_payouts
    GROUP BY 1,2
),
/* ----------------------------------------------------------------
   4. конвертируем → USD и агрегируем по дню
   ---------------------------------------------------------------- */
daily_sum AS (
    SELECT
        pc.payout_date,
        SUM(
            CASE
                WHEN pc.currency = 'USD'
                     THEN pc.payout_amount
                ELSE pc.payout_amount * c.exchange_ratio
            END
        ) AS payout_amount_usd
    FROM payouts_by_curr pc
    LEFT JOIN currencies c
           ON  c.exchange_date = pc.payout_date
          AND c.currency       = pc.currency
    GROUP BY pc.payout_date
)
/* ----------------------------------------------------------------
   5. итоговый вывод (фильтр по датам в самом низу)
   ---------------------------------------------------------------- */
SELECT
    payout_date                   AS "date",
    payout_amount_usd             AS amount,
    'USD'::text                   AS currency
FROM daily_sum ds
where
    (cast(:date_from as date) is null or ds.payout_date >= cast(:date_from as date))
    and (cast(:date_to as date) is null or ds.payout_date <= cast(:date_to as date))
ORDER BY payout_date;