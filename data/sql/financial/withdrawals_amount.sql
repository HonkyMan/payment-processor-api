/* ===============================================================
   Итоговая сумма вывводов средств (USD) по дням, по таблице WITHDRAWALS
   =============================================================== */

WITH currencies AS (                     -- 1. средний курс USD
    SELECT
        crh.currency::text                                   AS currency,       -- → text, чтобы не кастовать далее
        to_timestamp(crh.created_at)::date                   AS exchange_date,
        AVG(crh.usd_ratio)                                   AS exchange_ratio
    FROM currencies_rates_history crh
    GROUP BY crh.currency, to_timestamp(crh.created_at)::date
),
all_payouts as (
	select
		to_timestamp(w.create_date)::date payout_date,
		w.currency::text,
		w.amount,
		w.fee
	from 
		withdrawals w 
	join users u on u.id = w.user_id
	where
		w.status = 'PAID'
		and u.is_fake = false
),
payouts_by_curr as (
	select 
		ap.payout_date,
		ap.currency,
		sum(ap.amount - coalesce(ap.fee, 0)) / 100 as payout_amount
	from all_payouts as ap
	group by 1, 2
),
daily_payouts as (
	select 
		pbc.payout_date,
		sum(
            case
                when pbc.currency = 'USD'
                     then pbc.payout_amount
                else pbc.payout_amount * c.exchange_ratio
            end
        )  as payout_amount_usd
	from payouts_by_curr pbc
	left join currencies c
           on  c.exchange_date = pbc.payout_date
          and c.currency = pbc.currency
    group by pbc.payout_date
)
select 
	dp.payout_date 			as "date",
	dp.payout_amount_usd 	as amount,
	'USD'::text          	AS currency
from daily_payouts dp
where
    (cast(:date_from as date) is null or dp.payout_date >= cast(:date_from as date))
    and (cast(:date_to as date) is null or dp.payout_date <= cast(:date_to as date))
order by payout_date asc;