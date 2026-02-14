-- dimension: customers enriched with order stats
-- this is what you'd build in dbt as a mart for reporting

DROP TABLE IF EXISTS dim_customers;

CREATE TABLE dim_customers AS
SELECT
    c.customer_id,
    c.full_name,
    c.email,
    c.acquisition_channel,
    c.city,
    c.state,
    c.created_at AS first_seen_at,
    c.last_active_at,
    c.days_active,
    strftime('%Y-%m', c.created_at) AS cohort_month,
    COALESCE(o.total_orders, 0) AS lifetime_orders,
    COALESCE(o.total_revenue, 0) AS lifetime_revenue,
    COALESCE(o.avg_order_value, 0) AS avg_order_value,
    o.first_order_date,
    o.last_order_date,
    CASE
        WHEN o.total_orders IS NULL THEN 'never_purchased'
        WHEN o.total_orders = 1 THEN 'one_time'
        WHEN o.total_orders BETWEEN 2 AND 4 THEN 'repeat'
        ELSE 'loyal'
    END AS customer_segment,
    CASE
        WHEN o.last_order_date IS NULL THEN 'no_purchase'
        WHEN julianday('now') - julianday(o.last_order_date) <= 30 THEN 'active'
        WHEN julianday('now') - julianday(o.last_order_date) <= 90 THEN 'at_risk'
        ELSE 'churned'
    END AS activity_status
FROM stg_customers c
LEFT JOIN (
    SELECT
        customer_id,
        COUNT(*) AS total_orders,
        ROUND(SUM(total), 2) AS total_revenue,
        ROUND(AVG(total), 2) AS avg_order_value,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date
    FROM stg_orders
    GROUP BY customer_id
) o ON c.customer_id = o.customer_id
