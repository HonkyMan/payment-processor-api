/* ===============================================================
   Paying users daily (USD)
   =============================================================== */
with good_users as (
    select 
        u.id user_id
    from users u
    where 
        u.is_fake = false
        and to_timestamp(u.date_of_registration)::date >= '2022-01-01'
),
deposit_users as (
    select 
        to_timestamp(d."timestamp")::date deposit_date,
        count(distinct d.user_id) as paying_users
    from 
        deposits d
    join good_users u on u.user_id = d.user_id
    where d.status = 'ENROLLED'
    group by 1
)
SELECT 
    deposit_date as "date",
    paying_users active_users
FROM deposit_users
WHERE
    (cast(:date_from as date) is null or deposit_date >= cast(:date_from as date))
    and (cast(:date_to as date) is null or deposit_date <= cast(:date_to as date))
ORDER BY deposit_date ASC;