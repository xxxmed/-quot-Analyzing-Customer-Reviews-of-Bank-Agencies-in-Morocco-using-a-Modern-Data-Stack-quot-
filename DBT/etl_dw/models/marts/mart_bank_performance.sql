{{
    config(
        materialized='table'
    )
}}

with int_reviews as (
    select * from {{ ref('int_bank_reviews') }}
),

bank_metrics as (
    select
        bank_name,
        branch_name,
        location,
        review_year,
        review_month,
        count(*) as total_reviews,
        avg(rating) as avg_rating,
        count(case when sentiment = 'Positive' then 1 end) as positive_reviews,
        count(case when sentiment = 'Neutral' then 1 end) as neutral_reviews,
        count(case when sentiment = 'Negative' then 1 end) as negative_reviews,
        -- Calculate percentages
        round(count(case when sentiment = 'Positive' then 1 end)::numeric / count(*) * 100, 2) as positive_percentage,
        round(count(case when sentiment = 'Neutral' then 1 end)::numeric / count(*) * 100, 2) as neutral_percentage,
        round(count(case when sentiment = 'Negative' then 1 end)::numeric / count(*) * 100, 2) as negative_percentage
    from int_reviews
    group by 
        bank_name,
        branch_name,
        location,
        review_year,
        review_month
)

select * from bank_metrics 