-- staging layer: clean up raw customer data
-- basically just renaming cols and standardizing types

DROP TABLE IF EXISTS stg_customers;

CREATE TABLE stg_customers AS
SELECT
    customer_id,
    email,
    first_name,
    last_name,
    first_name || ' ' || last_name AS full_name,
    LOWER(acquisition_channel) AS acquisition_channel,
    city,
    state,
    created_at,
    last_active_at,
    CAST(julianday(last_active_at) - julianday(created_at) AS INTEGER) AS days_active
FROM raw_customers
WHERE customer_id IS NOT NULL
