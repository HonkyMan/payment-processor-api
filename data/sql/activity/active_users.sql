with good_users as (
    select 
        u.id user_id
    from users u
    where 
        u.is_fake = false
        and to_timestamp(u.date_of_registration)::date >= '2022-01-01'
),
sport_bets as (
    select 
        to_timestamp(b."timestamp")::date bet_date,
        count(distinct b.user_id) as active_users
    from 
        betslips b
    join good_users u on u.user_id = b.user_id
    group by 1
),
casino_st_bets as (
    select 
        st."timestamp"::date bet_date,
        count(distinct st.user_id) as active_users
    FROM
        slotegrator_transactions st
    JOIN good_users u ON u.user_id = st.user_id
    WHERE st.type = 'BET'
    GROUP BY 1
),
casino_op_bets as (
    select 
        to_timestamp(t.created_at)::date bet_date,
        count(distinct t.user_id) as active_users
    FROM
        casino_transaction_only_play t
    JOIN good_users u ON u.user_id = t.user_id
    WHERE t.type = 'BET'
    GROUP BY 1
),
casino_cb_bets as (
    select 
        t.created_at::date bet_date,
        count(distinct t.user_id) as active_users
    FROM
        casino_transaction_claw_buster t
    JOIN good_users u ON u.user_id = t.user_id
    WHERE t.type = 'BET'
    GROUP BY 1
),
casino_io_bets as (
    select 
        t.created_at::date bet_date,
        count(distinct t.user_id) as active_users
    FROM
        casino_transaction_inout t
    JOIN good_users u ON u.user_id = t.user_id
    WHERE t.type = 'BET'
    GROUP BY 1
),
casino_ngs_bets as (
    select 
        t.created_at::date bet_date,
        count(distinct t.user_id) as active_users
    FROM
        casino_transaction_nexgenspin t
    JOIN good_users u ON u.user_id = t.user_id
    WHERE t.type = 'BET'
    GROUP BY 1
),
deposit_users as (
    select 
        to_timestamp(d."timestamp")::date deposit_date,
        count(distinct d.user_id) as active_users
    from 
        deposits d
    join good_users u on u.user_id = d.user_id
    where d.status = 'ENROLLED'
    group by 1
),
withdrawal_users as (
    select 
        to_timestamp(w.create_date)::date withdrawal_date,
        count(distinct w.user_id) as active_users
    from 
        withdrawals w
    join good_users u on u.user_id = w.user_id
    where w.status = 'PAID'
    group by 1
),
daily_active_users as (
    select 
        "date",
        sum(users) as active_users
    from (
        select bet_date "date", active_users users from sport_bets
        union all
        select bet_date "date", active_users users from casino_st_bets
        union all
        select bet_date "date", active_users users from casino_op_bets
        union all
        select bet_date "date", active_users users from casino_cb_bets
        union all
        select bet_date "date", active_users users from casino_io_bets
        union all
        select bet_date "date", active_users users from casino_ngs_bets
        union all
        select deposit_date "date", active_users users from deposit_users
        union all
        select withdrawal_date "date", active_users users from withdrawal_users
    ) as daily_active
    group by 1
)
select 
    "date",
    active_users
from daily_active_users
WHERE
    (cast(:date_from as date) is null or "date" >= cast(:date_from as date))
    and (cast(:date_to as date) is null or "date" <= cast(:date_to as date))
order by "date" asc;