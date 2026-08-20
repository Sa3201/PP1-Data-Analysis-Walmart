{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='store_id',
        on_schema_change='sync_all_columns'
    )
}}

with source as (
    select store_id, store_type, store_size
    from {{ ref('stg_walmart_stores') }}
),

{% if is_incremental() %}
existing as (
    select store_id, store_type, store_size, insert_date, update_date
    from {{ this }}
),
{% endif %}

final as (
    select
        source.store_id,
        source.store_type,
        source.store_size,
        {% if is_incremental() %}
        coalesce(existing.insert_date, current_timestamp()) as insert_date,
        case
            when existing.store_id is null then current_timestamp()
            when source.store_type is distinct from existing.store_type
              or source.store_size is distinct from existing.store_size
                then current_timestamp()
            else existing.update_date
        end as update_date
        {% else %}
        current_timestamp() as insert_date,
        current_timestamp() as update_date
        {% endif %}
    from source
    {% if is_incremental() %}
    left join existing using (store_id)
    {% endif %}
)

select * from final

