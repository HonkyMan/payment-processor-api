/* ============================================================
   Сумма ставок в USD по дням (WIN/LOSE/CASHOUT из betslips)
   ============================================================ */

WITH currencies AS (                       -- 1. курс «день-валюта → USD»
    SELECT
        crh.currency::text                                   AS currency,
        to_timestamp(crh.created_at)::date                   AS exchange_date,
        AVG(crh.usd_ratio)                                   AS exchange_ratio
    FROM currencies_rates_history crh
    GROUP BY crh.currency, to_timestamp(crh.created_at)::date
),
bets_by_curr AS (                         -- 2. ставки сгруппированы по (дата, валюта)
    SELECT
        to_timestamp(b."timestamp")::date      AS bet_date,
        b.currency::text                       AS currency,
        SUM(b.sum)::numeric / 100              AS bet_amount
    FROM betslips b
    left join users u on 
    					u.id = b.user_id
    WHERE 
    	b.status IN ('WIN', 'LOSE', 'CASHOUT')
    	and u.is_fake = false
    GROUP BY 1, 2
)
SELECT                                       -- 3. конвертируем и суммируем по дню
    bc.bet_date as "date",
    SUM(
        CASE
            WHEN bc.currency = 'USD'
                 THEN bc.bet_amount
            ELSE bc.bet_amount * c.exchange_ratio
        END
    ) as amount,
    'USD'::text          AS currency
FROM bets_by_curr bc
LEFT JOIN currencies c
       ON  c.exchange_date = bc.bet_date
      AND c.currency      = bc.currency          -- курс может отсутствовать
WHERE
    (cast(:date_from as date) is null or bc.bet_date >= cast(:date_from as date))
    and (cast(:date_to as date) is null or bc.bet_date <= cast(:date_to as date))
GROUP BY bc.bet_date
ORDER BY bc.bet_date ASC;