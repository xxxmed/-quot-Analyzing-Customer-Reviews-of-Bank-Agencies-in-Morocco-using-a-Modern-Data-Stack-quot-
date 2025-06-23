# Analyzing Customer Reviews of Bank Agencies in Morocco using a Modern Data Stack

## Project Overview

This project aims to build a complete and automated data pipeline to collect, transform, and analyze customer reviews of bank agencies in Morocco. The reviews were extracted from Google Maps using the Google Places API and processed using a modular and scalable data stack.

---

## Objectives

- Collect online customer reviews for major Moroccan bank agencies
- Build a robust ETL pipeline with orchestration and transformation
- Design a star schema for the analytical data warehouse
- Perform sentiment analysis and extract KPIs
- Visualize the insights through interactive dashboards

---

## Tools & Technologies

| Layer            | Technology                     |
|------------------|--------------------------------|
| Extraction       | Python, Google Maps API        |
| Storage          | PostgreSQL                     |
| Transformation   | DBT (Data Build Tool)          |
| Orchestration    | Apache Airflow                 |
| Visualization    | Looker Studio                  |

---

## Pipeline Architecture

1. **Data Extraction**  
   Python script scrapes reviews via the Google Places API, with multithreaded processing and UTF-8 cleaning.

2. **Staging & Loading**  
   Extracted data is loaded into a PostgreSQL staging table using psycopg2.

3. **Transformation**  
   DBT models clean, enrich, and structure the data into a star schema with sentiment classification.

4. **Orchestration**  
   An Apache Airflow DAG manages extraction, loading, and transformation as daily scheduled tasks.

5. **Visualization**  
   Looker Studio dashboards display satisfaction trends by city, agency, and time, with filtering capabilities.

---

## Data Model

The warehouse is organized as a **star schema**:

- **Fact Table**: `Fait_Avis`  
- **Dimensions**:  
  - `Dim_Banque`  
  - `Dim_Agence`  
  - `Dim_Localisation`  
  - `Dim_Date`  
  - `Dim_Sentiment`

---

## Sample Analytical Queries

```sql
SELECT 
  b.nom_banque, 
  s.label_sentiment, 
  COUNT(f.id_avis) AS nb_avis, 
  AVG(f.note) AS note_moyenne
FROM fait_avis f
JOIN dim_banque b ON f.id_banque = b.id_banque
JOIN dim_sentiment s ON f.id_sentiment = s.id_sentiment
GROUP BY b.nom_banque, s.label_sentiment;
