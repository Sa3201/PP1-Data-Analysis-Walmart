select store_id, week_date
from {{ ref('int_store_weekly_sales') }}
group by store_id, week_date
having count(*) > 1

