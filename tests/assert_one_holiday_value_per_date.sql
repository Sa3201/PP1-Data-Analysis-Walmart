with holiday_values as (
    select week_date, is_holiday
    from {{ ref('stg_walmart_department_sales') }}

    union all

    select week_date, is_holiday
    from {{ ref('stg_walmart_features') }}
)

select week_date
from holiday_values
group by week_date
having count(distinct is_holiday) > 1

