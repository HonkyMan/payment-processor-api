/* ===============================================================
   Итоговая сумма ставок (USD) по дням, во всех казино-таблицах
   =============================================================== */

WITH currencies AS (                     -- 1. средний курс USD
    SELECT
        crh.currency::text                                   AS currency,       -- → text, чтобы не кастовать далее
        to_timestamp(crh.created_at)::date                   AS exchange_date,
        AVG(crh.usd_ratio)                                   AS exchange_ratio
    FROM currencies_rates_history crh
    GROUP BY crh.currency, to_timestamp(crh.created_at)::date
),
all_bets_raw AS (                     -- 2. собираем все «BET»-транзакции

    /* -------- slotegrator_transactions ------------------------ */
    SELECT
        st."timestamp"::date                              AS bet_date,
        st.amount                                         AS amount,
        u.currency::text                                  AS currency
    FROM slotegrator_transactions st
    JOIN users u       ON u.id = st.user_id
    WHERE st.type  = 'BET'
      AND u.is_fake = FALSE

    UNION ALL

    /* -------- casino_transaction_only_play -------------------- */
    SELECT
        to_timestamp(t.created_at)::date                  AS bet_date,
        t.amount                                          AS amount,
        u.currency::text                                  AS currency
    FROM casino_transaction_only_play t
    JOIN users u       ON u.id = t.user_id
    WHERE t.type  = 'BET'
      AND u.is_fake = FALSE
      AND NOT EXISTS (                                    -- исключаем отменённые ставки
            SELECT 1
            FROM casino_transaction_only_play c
            WHERE c.type = 'CANCEL'
              AND c.parent_transaction_id = t.transaction_id
      )

    UNION ALL

    /* -------- casino_transaction_claw_buster ------------------ */
    SELECT
        t.created_at::date                                AS bet_date,
        t.amount                                          AS amount,
        u.currency::text                                  AS currency
    FROM casino_transaction_claw_buster t
    JOIN users u       ON u.id = t.user_id
    WHERE t.type  = 'BET'
      AND u.is_fake = FALSE

    UNION ALL

    /* -------- casino_transaction_inout ------------------------ */
    SELECT
        t.created_at::date                                AS bet_date,
        t.amount                                          AS amount,
        u.currency::text                                  AS currency
    FROM casino_transaction_inout t
    JOIN users u       ON u.id = t.user_id
    WHERE t.type  = 'BET'
      AND u.is_fake = FALSE

    UNION ALL

    /* -------- casino_transaction_nexgenspin ------------------- */
    SELECT
        t.created_at::date                                AS bet_date,
        t.amount                                          AS amount,
        u.currency::text                                  AS currency
    FROM casino_transaction_nexgenspin t
    JOIN users u       ON u.id = t.user_id
    WHERE t.type  = 'BET'
      AND u.is_fake = FALSE
),
bets_by_curr AS (                     -- 3. агрегируем в валюте игрока
    SELECT
        bet_date,
        currency,
        SUM(amount)::numeric / 100                        AS bet_amount        -- делим на 100 «копеек»
    FROM all_bets_raw
    GROUP BY bet_date, currency
),
daily_sum AS (                        -- 4. конвертация → USD и сумма по дню
    SELECT
        bc.bet_date,
        SUM(
            CASE
                WHEN bc.currency = 'USD'
                     THEN bc.bet_amount
                ELSE bc.bet_amount * c.exchange_ratio
            END
        )                                               AS bet_amount_usd
    FROM bets_by_curr bc
    LEFT JOIN currencies c
           ON  c.exchange_date = bc.bet_date
          AND c.currency       = bc.currency
    GROUP BY bc.bet_date
)
SELECT
    bet_date as "date",
    bet_amount_usd as amount,
    'USD'::text          AS currency
FROM daily_sum
WHERE
    (cast(:date_from as date) is null or bet_date >= cast(:date_from as date))
    and (cast(:date_to as date) is null or bet_date <= cast(:date_to as date))
ORDER BY bet_date;