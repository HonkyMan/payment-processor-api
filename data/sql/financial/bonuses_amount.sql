/* ===============================================================
   Итоговая сумма отыгранных бонусов (USD) пользователей 
   =============================================================== */


WITH currencies AS (                     -- 1. средний курс USD
    SELECT
        crh.currency::text                                   AS currency,       -- → text, чтобы не кастовать далее
        to_timestamp(crh.created_at)::date                   AS exchange_date,
        AVG(crh.usd_ratio)                                   AS exchange_ratio
    FROM currencies_rates_history crh
    GROUP BY crh.currency, to_timestamp(crh.created_at)::date
),
all_bonuses as (
	select 
		to_timestamp(b.created_date)::date bonuse_date,
		b.amount_won bonus_amount,
		u.currency::text currency
	from
		bonuses b
	left join 
		users u 
			on u.id = b.user_id
	where 
		b.status = 'DONE'
		and u.is_fake = false
		and b."type" in (	
							'CASHBACK_CASINO', 'CASINO_FREESPIN', 'CASINO_FREESPIN_OP', 'CASINO_FREESPIN_S', 'FREEMONEY_CASINO', 'CASINO_FREESPIN_IO', 
							'CASHBACK_SPORT', 'FREEMONEY_SPORT', 'SPORT_FREE_MONEY', 'SPORT_NO_RISK', 'SPORT_COMBOBOOST', 'SPORT_REFUND', 
							'FREEMONEY_LIVE', 'REFERRAL_DEPOSIT', 'REFERRAL'
						)
),
bonuses_by_date as (
	select 
		ab.bonuse_date,
		ab.currency,
		sum(ab.bonus_amount) / 100 bonus_amount
	from 
		all_bonuses ab
	group by 1, 2
),
daily_bonuses as (
	select 
		bbd.bonuse_date,
		sum(
            case
                when bbd.currency = 'USD'
                     then bbd.bonus_amount
                else bbd.bonus_amount * c.exchange_ratio
            end
        )  as bonus_amount_usd
	from bonuses_by_date bbd
	left join currencies c
           on  c.exchange_date = bbd.bonuse_date
          and c.currency = bbd.currency
    group by bbd.bonuse_date
)
select 
	db.bonuse_date          as "date",
	db.bonus_amount_usd     as amount,
    'USD'::text             AS currency
from daily_bonuses db
WHERE
    (cast(:date_from as date) is null or bonuse_date >= cast(:date_from as date))
    and (cast(:date_to as date) is null or bonuse_date <= cast(:date_to as date))
order by bonuse_date asc;