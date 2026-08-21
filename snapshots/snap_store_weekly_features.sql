{% snapshot snap_store_weekly_features %}

{{
    config(
        target_schema='snapshots',
        unique_key='store_week_key',
        strategy='check',
        check_cols=[
            'temperature',
            'fuel_price',
            'markdown_1',
            'markdown_2',
            'markdown_3',
            'markdown_4',
            'markdown_5',
            'cpi',
            'unemployment',
            'is_holiday'
        ],
        invalidate_hard_deletes=True
    )
}}

select
    store_week_key,
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
from {{ ref('stg_walmart_features') }}

{% endsnapshot %}
