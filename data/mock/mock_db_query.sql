select 
    d.closed_at::date as deposit_date,
    sum(d.amount)::numeric / 100 as deposit_amount,
from 
    deposits d
where 
    d,status = 'SUCCESS'