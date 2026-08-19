with all_dates as (
    select week_date, is_holiday
    from {{ ref('stg_walmart_department_sales') }}

    union all

    select week_date, is_holiday
    from {{ ref('stg_walmart_features') }}
)

select
    week_date,
    boolor_agg(is_holiday) as is_holiday
from all_dates
group by week_date
