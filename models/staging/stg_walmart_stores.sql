with source as (
    select * from {{ source('walmart_raw', 'walmart_stores_raw') }}
),

renamed as (
    select
        cast(store_id as integer) as store_id,
        upper(trim(store_type)) as store_type,
        cast(store_size as integer) as store_size
    from source
),

deduplicated as (
    select *
    from renamed
    qualify row_number() over (
        partition by store_id
        order by store_type, store_size desc
    ) = 1
)

select * from deduplicated

