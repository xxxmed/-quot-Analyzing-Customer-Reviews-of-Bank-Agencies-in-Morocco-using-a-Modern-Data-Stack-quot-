{{
    config(
        materialized='view'
    )
}}

with source as (
    select * from {{ source('raw', 'bank_reviews') }}
),

-- Remove duplicates based on all columns
deduplicated as (
    select distinct
        bank_name,
        branch_name,
        location,
        review_text,
        rating,
        review_date
    from source
),

-- Handle missing values
cleaned as (
    select
        coalesce(bank_name, 'Unknown Bank') as bank_name,
        coalesce(branch_name, 'Unknown Branch') as branch_name,
        coalesce(location, 'Unknown Location') as location,
        coalesce(review_text, '') as review_text,
        coalesce(rating, 3) as rating,  -- Default to neutral rating
        coalesce(review_date, current_date) as review_date
    from deduplicated
)

select * from cleaned