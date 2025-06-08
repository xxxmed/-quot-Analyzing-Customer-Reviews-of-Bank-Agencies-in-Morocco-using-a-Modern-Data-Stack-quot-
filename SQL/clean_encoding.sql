-- First, let's see what problematic characters we have
SELECT DISTINCT bank_name, branch_name, location
FROM bank_reviews
WHERE 
    bank_name LIKE '%Ã%' OR 
    bank_name LIKE '%Â%' OR
    bank_name LIKE '%é%' OR
    branch_name LIKE '%Ã%' OR 
    branch_name LIKE '%Â%' OR
    branch_name LIKE '%é%' OR
    location LIKE '%Ã%' OR 
    location LIKE '%Â%' OR
    location LIKE '%é%';

-- Create a function to clean the text
CREATE OR REPLACE FUNCTION clean_text(input_text TEXT) 
RETURNS TEXT AS $BODY$
DECLARE
    result TEXT;
BEGIN
    -- First, convert any existing UTF-8 characters to their proper form
    result := input_text;
    
    -- Handle the specific byte 0xe9 (é) and similar cases
    result := REPLACE(result, E'\xC3\xA9', 'é');  -- UTF-8 é
    result := REPLACE(result, E'\xC3\xA8', 'è');  -- UTF-8 è
    result := REPLACE(result, E'\xC3\xA0', 'à');  -- UTF-8 à
    result := REPLACE(result, E'\xC3\xA7', 'ç');  -- UTF-8 ç
    result := REPLACE(result, E'\xC3\xB4', 'ô');  -- UTF-8 ô
    result := REPLACE(result, E'\xC3\xB9', 'ù');  -- UTF-8 ù
    result := REPLACE(result, E'\xC3\xBB', 'û');  -- UTF-8 û
    result := REPLACE(result, E'\xC3\xAF', 'ï');  -- UTF-8 ï
    result := REPLACE(result, E'\xC3\xAB', 'ë');  -- UTF-8 ë
    result := REPLACE(result, E'\xC3\xA2', 'â');  -- UTF-8 â
    result := REPLACE(result, E'\xC3\xAA', 'ê');  -- UTF-8 ê
    result := REPLACE(result, E'\xC3\xAE', 'î');  -- UTF-8 î
    
    -- Handle double-encoded cases
    result := REPLACE(result, 'Ã©', 'é');
    result := REPLACE(result, 'Ã¨', 'è');
    result := REPLACE(result, 'Ã', 'à');
    result := REPLACE(result, 'Ã§', 'ç');
    result := REPLACE(result, 'Ã´', 'ô');
    result := REPLACE(result, 'Ã¹', 'ù');
    result := REPLACE(result, 'Ã»', 'û');
    result := REPLACE(result, 'Ã¯', 'ï');
    result := REPLACE(result, 'Ã«', 'ë');
    result := REPLACE(result, 'Ã¢', 'â');
    result := REPLACE(result, 'Ãª', 'ê');
    result := REPLACE(result, 'Ã®', 'î');
    
    -- Handle Â cases
    result := REPLACE(result, 'Â©', 'é');
    result := REPLACE(result, 'Â¨', 'è');
    result := REPLACE(result, 'Â', 'à');
    result := REPLACE(result, 'Â§', 'ç');
    result := REPLACE(result, 'Â´', 'ô');
    result := REPLACE(result, 'Â¹', 'ù');
    result := REPLACE(result, 'Â»', 'û');
    result := REPLACE(result, 'Â¯', 'ï');
    result := REPLACE(result, 'Â«', 'ë');
    result := REPLACE(result, 'Â¢', 'â');
    result := REPLACE(result, 'Âª', 'ê');
    result := REPLACE(result, 'Â®', 'î');
    
    -- Handle specific problematic cases
    result := REPLACE(result, 'Âï', 'ï');
    result := REPLACE(result, 'Âî', 'î');
    
    -- Convert to proper UTF-8
    BEGIN
        result := convert_to(convert_from(result::bytea, 'UTF8'), 'UTF8');
    EXCEPTION WHEN OTHERS THEN
        -- If conversion fails, return the cleaned text as is
        NULL;
    END;
    
    RETURN result;
END;
$BODY$ LANGUAGE plpgsql;

-- Update the table with cleaned text
UPDATE bank_reviews
SET 
    bank_name = clean_text(bank_name),
    branch_name = clean_text(branch_name),
    location = clean_text(location),
    review_text = clean_text(review_text);

-- Verify the changes
SELECT DISTINCT bank_name, branch_name, location
FROM bank_reviews
WHERE 
    bank_name LIKE '%Ã%' OR 
    bank_name LIKE '%Â%' OR
    bank_name LIKE '%é%' OR
    branch_name LIKE '%Ã%' OR 
    branch_name LIKE '%Â%' OR
    branch_name LIKE '%é%' OR
    location LIKE '%Ã%' OR 
    location LIKE '%Â%' OR
    location LIKE '%é%';

-- Drop the function if you don't need it anymore
-- DROP FUNCTION clean_text(TEXT); 