select
    store_id,
    week_date,
    boolor_agg(is_holiday) as is_holiday,
    sum(weekly_sales) as weekly_sales
from {{ ref('stg_walmart_department_sales') }}
group by store_id, week_date