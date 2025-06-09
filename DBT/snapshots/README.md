# Snapshots Directory

This directory is for tracking changes in your data over time.
Snapshots help you maintain historical records of your data.

Use cases:
- Tracking changes in customer information
- Maintaining historical records of reviews
- Auditing data changes
- Type 2 slowly changing dimensions

To use snapshots:
1. Create a snapshot file (e.g., `snapshots/bank_reviews_snapshot.sql`)
2. Define your snapshot strategy
3. Run `dbt snapshot` to capture changes 