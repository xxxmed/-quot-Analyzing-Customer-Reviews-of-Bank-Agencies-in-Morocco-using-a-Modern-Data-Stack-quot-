

with location_reviews as (
    select 
    
        bank_name,
        location,
        string_agg(cleaned_text, ' ') as concatenated_text,
        count(*) as review_count,
        round(avg(rating)::numeric, 2) as avg_rating,
        min(rating) as min_rating,
        max(rating) as max_rating,
        count(case when rating >= 4 then 1 end) as positive_reviews,
        count(case when rating <= 2 then 1 end) as negative_reviews
    from "DataWare"."public"."int_bank_reviews"
    where cleaned_text is not null
    group by location, bank_name
)

select 
    bank_name,
    location,
    concatenated_text,
    review_count,
    avg_rating,
    min_rating,
    max_rating,
    positive_reviews,
    negative_reviews,
    round((positive_reviews::float / review_count * 100)::numeric, 2) as positive_review_percentage,
    round((negative_reviews::float / review_count * 100)::numeric, 2) as negative_review_percentage
from location_reviews
order by bank_name,location