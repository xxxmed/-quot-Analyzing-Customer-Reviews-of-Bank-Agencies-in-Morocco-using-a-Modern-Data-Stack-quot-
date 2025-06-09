# Seeds Directory

This directory is for static data files that you want to load into your data warehouse.
These are typically CSV files that contain reference data or small lookup tables.

Example usage:
- Reference data
- Lookup tables
- Static mappings
- Configuration data

To use seeds:
1. Place your CSV files in this directory
2. Reference them in your models using {{ ref('seed_name') }}
3. Run `dbt seed` to load them into your data warehouse 