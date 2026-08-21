with current_features as (
    select store_week_key
    from {{ ref('fct_store_weekly_features') }}
    where is_current
)

select staging.store_week_key
from {{ ref('stg_walmart_features') }} as staging
left join current_features
    on staging.store_week_key = current_features.store_week_key
group by staging.store_week_key
having count(current_features.store_week_key) != 1
