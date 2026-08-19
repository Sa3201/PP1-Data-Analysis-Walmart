with staging_total as (
    select round(sum(weekly_sales), 2) as weekly_sales
    from {{ ref('stg_walmart_department_sales') }}
),

mart_total as (
    select round(sum(weekly_sales), 2) as weekly_sales
    from {{ ref('fct_department_weekly_sales') }}
    where is_current
)

select
    staging_total.weekly_sales as staging_weekly_sales,
    mart_total.weekly_sales as mart_weekly_sales
from staging_total
cross join mart_total
where staging_total.weekly_sales != mart_total.weekly_sales

