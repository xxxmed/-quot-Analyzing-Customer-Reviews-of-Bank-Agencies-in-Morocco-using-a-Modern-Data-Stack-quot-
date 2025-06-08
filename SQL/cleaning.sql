-- This script updates bank names in the bank_reviews table to correct encoding issues
-- It replaces incorrectly encoded special characters (Ã©, Ã¨, etc.) with their proper UTF-8 equivalents
-- The updates ensure consistent and readable bank names across the database


UPDATE bank_reviews
SET bank_name = 'Crédit Agricole du Maroc'
WHERE bank_name='CrÃ©dit Agricole du Maroc';

UPDATE bank_reviews
SET bank_name = 'Crédit du Maroc'
WHERE bank_name='CrÃ©dit du Maroc';

UPDATE bank_reviews
SET bank_name = 'Société Générale Maroc'
WHERE bank_name='SociÃ©tÃ© GÃ©nÃ©rale Maroc';

UPDATE bank_reviews
SET
    location = REPLACE(location, 'Ã©', 'é'),
    branch_name = REPLACE(branch_name, 'Ã©', 'é')
WHERE  location LIKE '%Ã©%' or branch_name LIKE '%Ã©%';

UPDATE bank_reviews
SET
    location = REPLACE(location, 'Ã¨', 'è'),
    branch_name = REPLACE(branch_name, 'Ã¨', 'è')
WHERE  location LIKE '%Ã¨%' or branch_name LIKE '%Ã¨%';