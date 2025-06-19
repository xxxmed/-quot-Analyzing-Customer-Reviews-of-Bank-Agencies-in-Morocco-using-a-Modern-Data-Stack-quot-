-- SQL script to create all tables for the Data Warehouse (bank_reviews_dw)
-- This script includes staging, dimension, fact, mart, and analysis tables
-- Adjust schema names as needed for your cloud environment

-- 0. Create Schemas (if not exist)
CREATE SCHEMA IF NOT EXISTS public_public_staging;
CREATE SCHEMA IF NOT EXISTS public_public_intermediate;
CREATE SCHEMA IF NOT EXISTS public_public_marts;

-- 1. Staging Table: Raw Bank Reviews
CREATE TABLE IF NOT EXISTS public_public_staging.stg_bank_reviews (
    review_id SERIAL PRIMARY KEY,
    agency_name TEXT,
    agency_city TEXT,
    review_text TEXT,
    review_rating INTEGER,
    review_date DATE,
    source TEXT
);

-- 2. Dimension Table: Agencies
CREATE TABLE IF NOT EXISTS public_public_intermediate.dim_agency (
    agency_id SERIAL PRIMARY KEY,
    agency_name TEXT NOT NULL,
    agency_city TEXT NOT NULL
);

-- 3. Dimension Table: Dates
CREATE TABLE IF NOT EXISTS public_public_intermediate.dim_date (
    date_id SERIAL PRIMARY KEY,
    review_date DATE NOT NULL
);

-- 4. Fact Table: Reviews
CREATE TABLE IF NOT EXISTS public_public_intermediate.fact_reviews (
    review_id INTEGER PRIMARY KEY,
    agency_id INTEGER REFERENCES public_public_intermediate.dim_agency(agency_id),
    date_id INTEGER REFERENCES public_public_intermediate.dim_date(date_id),
    review_text TEXT,
    review_rating INTEGER,
    source TEXT
);

-- 5. Mart Table: Location Reviews (Aggregated)
CREATE TABLE IF NOT EXISTS public_public_marts.mart_location_reviews (
    agency_city TEXT,
    avg_rating FLOAT,
    review_count INTEGER
);

-- 6. Analysis Table: Sentiment Analysis Results (if used)
CREATE TABLE IF NOT EXISTS public_public_marts.analysis_sentiment (
    review_id INTEGER PRIMARY KEY,
    sentiment_label TEXT,
    sentiment_score FLOAT
);

-- 7. (Optional) Cleaned Reviews Table
CREATE TABLE IF NOT EXISTS public_public_staging.cleaned_bank_reviews (
    review_id INTEGER PRIMARY KEY,
    cleaned_text TEXT
);

-- Add more tables as needed for your analytics or marts
-- Make sure to create the schemas in your cloud database if they do not exist:
-- CREATE SCHEMA IF NOT EXISTS public_public_staging;
-- CREATE SCHEMA IF NOT EXISTS public_public_intermediate;
-- CREATE SCHEMA IF NOT EXISTS public_public_marts;

-- End of script
