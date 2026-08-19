with source as (
    select * from {{ source('walmart_raw', 'walmart_fact_raw') }}
),

renamed as (
    select
        cast(store_id as integer) as store_id,
        cast(date as date) as week_date,
        cast(temperature as number(8, 2)) as temperature,
        cast(fuel_price as number(8, 2)) as fuel_price,
        cast(markdown1 as number(18, 2)) as markdown_1,
        cast(markdown2 as number(18, 2)) as markdown_2,
        cast(markdown3 as number(18, 2)) as markdown_3,
        cast(markdown4 as number(18, 2)) as markdown_4,
        cast(markdown5 as number(18, 2)) as markdown_5,
        cast(cpi as number(10, 2)) as cpi,
        cast(unemployment as number(8, 2)) as unemployment,
        cast(isholiday as boolean) as is_holiday
    from source
),

deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by store_id, week_date
        order by temperature, fuel_price
    ) = 1
)

select
    {{ surrogate_key(['store_id', 'week_date']) }} as store_week_key,
    store_id,
    week_date,
    temperature,
    fuel_price,
    markdown_1,
    markdown_2,
    markdown_3,
    markdown_4,
    markdown_5,
    cpi,
    unemployment,
    is_holiday
from deduplicated

