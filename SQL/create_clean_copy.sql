-- First, create the new table with the same structure
CREATE TABLE bank_reviews_copy (
    id SERIAL PRIMARY KEY,
    bank_name TEXT,
    branch_name TEXT,
    location TEXT,
    review_text TEXT,
    rating INTEGER,
    review_date DATE,
    sentiment TEXT,
    sentiment_score FLOAT
);

-- Create a function to clean the text
CREATE OR REPLACE FUNCTION clean_text(input_text TEXT) 
RETURNS TEXT AS $BODY$
BEGIN
    -- Handle common encoding issues
    input_text := REPLACE(input_text, 'Ã©', 'é');
    input_text := REPLACE(input_text, 'Â©', 'é');
    input_text := REPLACE(input_text, 'Ã¨', 'è');
    input_text := REPLACE(input_text, 'Â¨', 'è');
    input_text := REPLACE(input_text, 'Ã', 'à');
    input_text := REPLACE(input_text, 'Â', 'à');
    input_text := REPLACE(input_text, 'Ã§', 'ç');
    input_text := REPLACE(input_text, 'Â§', 'ç');
    input_text := REPLACE(input_text, 'Ã´', 'ô');
    input_text := REPLACE(input_text, 'Â´', 'ô');
    input_text := REPLACE(input_text, 'Ã¹', 'ù');
    input_text := REPLACE(input_text, 'Â¹', 'ù');
    input_text := REPLACE(input_text, 'Ã»', 'û');
    input_text := REPLACE(input_text, 'Â»', 'û');
    input_text := REPLACE(input_text, 'Ã¯', 'ï');
    input_text := REPLACE(input_text, 'Â¯', 'ï');
    input_text := REPLACE(input_text, 'Ã«', 'ë');
    input_text := REPLACE(input_text, 'Â«', 'ë');
    input_text := REPLACE(input_text, 'Ã¢', 'â');
    input_text := REPLACE(input_text, 'Â¢', 'â');
    input_text := REPLACE(input_text, 'Ãª', 'ê');
    input_text := REPLACE(input_text, 'Âª', 'ê');
    input_text := REPLACE(input_text, 'Ã®', 'î');
    input_text := REPLACE(input_text, 'Â®', 'î');
    input_text := REPLACE(input_text, 'Âï', 'ï');
    input_text := REPLACE(input_text, 'Âî', 'î');
    
    -- Convert to proper UTF-8
    BEGIN
        input_text := convert_to(convert_from(input_text::bytea, 'UTF8'), 'UTF8');
    EXCEPTION WHEN OTHERS THEN
        -- If conversion fails, return the cleaned text as is
        NULL;
    END;
    
    RETURN input_text;
END;
$BODY$ LANGUAGE plpgsql;

-- Insert cleaned data into the new table
INSERT INTO bank_reviews_copy (
    bank_name,
    branch_name,
    location,
    review_text,
    rating,
    review_date,
    sentiment,
    sentiment_score
)
SELECT 
    clean_text(bank_name),
    clean_text(branch_name),
    clean_text(location),
    clean_text(review_text),
    rating,
    review_date,
    clean_text(sentiment),
    sentiment_score
FROM bank_reviews;

-- Verify the results
SELECT DISTINCT bank_name, branch_name, location
FROM bank_reviews_copy
WHERE 
    bank_name LIKE '%Ã%' OR 
    bank_name LIKE '%Â%' OR
    branch_name LIKE '%Ã%' OR 
    branch_name LIKE '%Â%' OR
    location LIKE '%Ã%' OR 
    location LIKE '%Â%';

-- Drop the function if you don't need it anymore
-- DROP FUNCTION clean_text(TEXT); 