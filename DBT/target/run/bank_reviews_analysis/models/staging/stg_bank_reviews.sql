
  create view "DataWare"."public"."stg_bank_reviews__dbt_tmp"
    
    
  as (
    

with source as (
    select * from "DataWare"."public"."bank_reviews"
),

-- Remove duplicates based on all columns
deduplicated as (
    select distinct
        id,
        bank_name,
        branch_name,
        location,
        review_text,
        rating,
        review_date,
        created_at
    from source
),

-- Handle missing values
cleaned as (
    select
        id,
        coalesce(bank_name, 'Unknown Bank') as bank_name,
        coalesce(branch_name, 'Unknown Branch') as branch_name,
        coalesce(location, 'Unknown Location') as location,
        coalesce(review_text, '') as review_text,
        coalesce(rating, 3) as rating,  -- Default to neutral rating
        coalesce(review_date, current_date) as review_date,
        coalesce(created_at, current_timestamp) as created_at
    from deduplicated
)

select * from cleaned
  );