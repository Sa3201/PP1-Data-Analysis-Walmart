{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='store_week_key',
        on_schema_change='sync_all_columns'
    )
}}

with source as (
    select
        store_week_key,
        store_id,
        cast(to_char(week_date, 'YYYYMMDD') as integer) as date_id,
        temperature,
        fuel_price,
        markdown_1,
        markdown_2,
        markdown_3,
        markdown_4,
        markdown_5,
        cpi,
        unemployment
    from {{ ref('stg_walmart_features') }}
),

{% if is_incremental() %}
existing as (
    select * from {{ this }}
),
{% endif %}

final as (
    select
        source.*,
        {% if is_incremental() %}
        coalesce(existing.insert_date, current_timestamp()) as insert_date,
        case
            when existing.store_week_key is null then current_timestamp()
            when source.temperature is distinct from existing.temperature
              or source.fuel_price is distinct from existing.fuel_price
              or source.markdown_1 is distinct from existing.markdown_1
              or source.markdown_2 is distinct from existing.markdown_2
              or source.markdown_3 is distinct from existing.markdown_3
              or source.markdown_4 is distinct from existing.markdown_4
              or source.markdown_5 is distinct from existing.markdown_5
              or source.cpi is distinct from existing.cpi
              or source.unemployment is distinct from existing.unemployment
                then current_timestamp()
            else existing.update_date
        end as update_date
        {% else %}
        current_timestamp() as insert_date,
        current_timestamp() as update_date
        {% endif %}
    from source
    {% if is_incremental() %}
    left join existing using (store_week_key)
    {% endif %}
)

select * from final

