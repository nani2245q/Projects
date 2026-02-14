-- CUSTOMER LIFETIME VALUE (LTV) ANALYSIS
-- estimate how much each customer segment is worth over time
-- useful for CAC vs LTV decisions

DROP TABLE IF EXISTS analytics_customer_ltv;

CREATE TABLE analytics_customer_ltv AS
SELECT
    customer_segment,
    acquisition_channel,
    COUNT(*) AS num_customers,
    ROUND(AVG(lifetime_revenue), 2) AS avg_ltv,
    ROUND(SUM(lifetime_revenue), 2) AS total_ltv,
    ROUND(AVG(lifetime_orders), 1) AS avg_orders,
    ROUND(AVG(avg_order_value), 2) AS avg_aov,
    -- avg days between first seen and last order
    ROUND(AVG(
        CASE WHEN last_order_date IS NOT NULL
            THEN julianday(last_order_date) - julianday(first_seen_at)
            ELSE 0
        END
    ), 0) AS avg_days_to_last_order,
    -- what % of customers in this segment actually bought something
    ROUND(
        CAST(SUM(CASE WHEN lifetime_orders > 0 THEN 1 ELSE 0 END) AS REAL) /
        COUNT(*) * 100, 2
    ) AS purchase_rate
FROM dim_customers
GROUP BY customer_segment, acquisition_channel
ORDER BY avg_ltv DESC
