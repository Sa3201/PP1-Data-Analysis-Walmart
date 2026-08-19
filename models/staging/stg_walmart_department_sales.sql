with source as (
    select * from {{ source('walmart_raw', 'walmart_department_raw') }}
),

renamed as (
    select
        cast(store_id as integer) as store_id,
        cast(dept_id as integer) as dept_id,
        cast(date as date) as week_date,
        cast(weekly_sales as number(18, 2)) as weekly_sales,
        cast(isholiday as boolean) as is_holiday
    from source
),

deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by store_id, dept_id, week_date
        order by weekly_sales desc, is_holiday desc
    ) = 1
)

select
    {{ surrogate_key(['store_id', 'dept_id', 'week_date']) }} as department_sales_key,
    store_id,
    dept_id,
    week_date,
    weekly_sales,
    is_holiday
from deduplicated

