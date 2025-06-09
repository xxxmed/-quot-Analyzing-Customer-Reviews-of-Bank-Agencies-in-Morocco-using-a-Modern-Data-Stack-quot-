/*
This model transforms bank review data by:
1. Normalizing text fields (lowercase, removing special characters, trimming whitespace)
2. Adding sentiment analysis based on rating scores
3. Extracting temporal components (year, month) for time-based analysis
4. Calculating review age in days

The model follows these steps:
- Starts with cleaned staging data (stg_bank_reviews)
- Applies text cleaning using the cleaned_text macro
- Adds derived fields for analysis
- Materializes as a table for better query performance
*/



with stg_reviews as (
    select * from "DataWare"."public"."stg_bank_reviews"
),

text_normalized as (
    select
        id,
        bank_name,
        branch_name,
        location,
        review_text,
        
    -- Convert to lowercase, remove special characters and numbers, clean whitespace
    trim(
        regexp_replace(
            regexp_replace(
                lower(coalesce(review_text, '')),
                '[^a-z\s]',  -- Remove special characters and numbers, keep only letters and spaces
                '',
                'g'
            ),
            '\s+',  -- Clean whitespace
            ' ',
            'g'
        )
    )
 as cleaned_text,
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
        cleaned_text,
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