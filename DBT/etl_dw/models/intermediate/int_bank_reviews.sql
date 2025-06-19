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
        bank_name,
        branch_name,
        location,
        review_text,
        lower(trim(review_text)) as normalized_text,
        rating,
        review_date
    from stg_reviews
),

transformed as (
    select
        bank_name,
        branch_name,
        location,
        review_text,
        normalized_text,
        rating,
        review_date,
        case 
            when rating >= 4 then 'Positive'
            when rating = 3 then 'Neutral'
            else 'Negative'
        end as sentiment,
        extract(year from review_date) as review_year,
        extract(month from review_date) as review_month,
        current_date - review_date as days_since_review
    from text_normalized
)

select * from transformed