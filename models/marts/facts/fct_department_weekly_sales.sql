select
    {{ surrogate_key(['department_sales_key', 'dbt_valid_from']) }} as department_sales_version_key,
    department_sales_key,
    store_id,
    dept_id,
    cast(to_char(week_date, 'YYYYMMDD') as integer) as date_id,
    weekly_sales,
    is_holiday,
    dbt_valid_from as vrsn_start_date,
    coalesce(dbt_valid_to, cast('9999-12-31 23:59:59' as timestamp)) as vrsn_end_date,
    dbt_valid_to is null as is_current,
    dbt_valid_from as insert_date,
    coalesce(dbt_valid_to, dbt_valid_from) as update_date
from {{ ref('snap_department_weekly_sales') }}

