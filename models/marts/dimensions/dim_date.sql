select
    cast(to_char(week_date, 'YYYYMMDD') as integer) as date_id,
    week_date,
    day(week_date) as day_of_month,
    dayname(week_date) as day_name,
    weekofyear(week_date) as week_of_year,
    month(week_date) as month_number,
    monthname(week_date) as month_name,
    quarter(week_date) as quarter_number,
    year(week_date) as year_number,
    is_holiday,
    current_timestamp() as insert_date,
    current_timestamp() as update_date
from {{ ref('int_calendar_dates') }}

