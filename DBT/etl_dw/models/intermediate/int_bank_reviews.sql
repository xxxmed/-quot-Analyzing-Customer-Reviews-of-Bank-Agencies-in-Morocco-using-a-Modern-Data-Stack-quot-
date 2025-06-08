/*
This model transforms bank review data by:
1. Normalizing text fields (lowercase, removing special characters, trimming whitespace)
2. Adding sentiment analysis based on rating scores
3. Extracting temporal components (year, month) for time-based analysis
4. Calculating review age in days

The model follows these steps:
- Starts with cleaned staging data (stg_bank_reviews)
- Applies text normalization using the normalize_text macro
- Adds derived fields for analysis
- Materializes as a table for better query performance
*/

{{
    config(
        materialized='table'
    )
}}

with stg_reviews as (
    select * from {{ ref('stg_bank_reviews') }}
),

text_normalized as (
    select
        id,
        bank_name,
        branch_name,
        location,
        review_text,
        {{ normalize_text('review_text') }},
        rating,
        review_date,
        created_at
    from stg_reviews
),

transformed as (
    select
        id,
        bank_name,
        branch_name,
        location,
        review_text,
        normalized_text,
        cleaned_text,
        trimmed_text,
        rating,
        review_date,
        created_at,
        -- Add some useful transformations
        case 
            when rating >= 4 then 'Positive'
            when rating = 3 then 'Neutral'
            else 'Negative'
        end as sentiment,
        -- Extract year and month for easier analysis
        extract(year from review_date) as review_year,
        extract(month from review_date) as review_month,
        -- Calculate days since review
        current_date - review_date as days_since_review
    from text_normalized
)

select * from transformed 