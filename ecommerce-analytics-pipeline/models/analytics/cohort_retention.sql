-- COHORT RETENTION ANALYSIS
-- group customers by signup month, track purchasing activity over time
-- this shows if customers stick around or churn

DROP TABLE IF EXISTS analytics_cohort_retention;

CREATE TABLE analytics_cohort_retention AS
SELECT
    c.cohort_month,
    o.order_month AS activity_month,
    COUNT(DISTINCT c.customer_id) AS active_customers,
    -- total customers in this cohort (for retention rate calc)
    cohort_size.total_in_cohort,
    ROUND(
        CAST(COUNT(DISTINCT c.customer_id) AS REAL) / cohort_size.total_in_cohort * 100, 2
    ) AS retention_rate,
    SUM(o.total) AS cohort_revenue,
    ROUND(AVG(o.total), 2) AS avg_order_value,
    -- months since cohort start
    CAST(
        (CAST(strftime('%Y', o.order_month || '-01') AS INTEGER) * 12 +
         CAST(strftime('%m', o.order_month || '-01') AS INTEGER)) -
        (CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER) * 12 +
         CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER))
    AS INTEGER) AS months_since_signup
FROM dim_customers c
JOIN stg_orders o ON c.customer_id = o.customer_id
JOIN (
    SELECT cohort_month, COUNT(*) AS total_in_cohort
    FROM dim_customers
    GROUP BY cohort_month
) cohort_size ON c.cohort_month = cohort_size.cohort_month
GROUP BY c.cohort_month, o.order_month, cohort_size.total_in_cohort
ORDER BY c.cohort_month, o.order_month
