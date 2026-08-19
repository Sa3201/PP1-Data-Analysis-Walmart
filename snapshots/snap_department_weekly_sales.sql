{% snapshot snap_department_weekly_sales %}

{{
    config(
        target_schema='snapshots',
        unique_key='department_sales_key',
        strategy='check',
        check_cols=['weekly_sales', 'is_holiday'],
        invalidate_hard_deletes=True
    )
}}

select
    department_sales_key,
    store_id,
    dept_id,
    week_date,
    weekly_sales,
    is_holiday
from {{ ref('stg_walmart_department_sales') }}

{% endsnapshot %}

