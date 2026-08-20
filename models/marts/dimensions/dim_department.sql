{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='dept_id',
        on_schema_change='sync_all_columns'
    )
}}

with source as (
    select distinct
        dept_id,
        'Department ' || cast(dept_id as varchar) as department_name
    from {{ ref('stg_walmart_department_sales') }}
),

{% if is_incremental() %}
existing as (
    select dept_id, department_name, insert_date, update_date
    from {{ this }}
),
{% endif %}

final as (
    select
        source.dept_id,
        source.department_name,
        {% if is_incremental() %}
        coalesce(existing.insert_date, current_timestamp()) as insert_date,
        case
            when existing.dept_id is null then current_timestamp()
            when source.department_name is distinct from existing.department_name
                then current_timestamp()
            else existing.update_date
        end as update_date
        {% else %}
        current_timestamp() as insert_date,
        current_timestamp() as update_date
        {% endif %}
    from source
    {% if is_incremental() %}
    left join existing using (dept_id)
    {% endif %}
)

select * from final