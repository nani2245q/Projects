-- REVENUE TRENDS
-- monthly revenue with growth rates, new vs returning customer split

DROP TABLE IF EXISTS analytics_revenue_trends;

CREATE TABLE analytics_revenue_trends AS
WITH monthly AS (
    SELECT
        order_month,
        COUNT(*) AS orders,
        COUNT(DISTINCT customer_id) AS unique_customers,
        ROUND(SUM(total), 2) AS revenue,
        ROUND(AVG(total), 2) AS avg_order_value,
        SUM(CASE WHEN is_first_order = 1 THEN total ELSE 0 END) AS new_customer_revenue,
        SUM(CASE WHEN is_first_order = 0 THEN total ELSE 0 END) AS returning_customer_revenue,
        SUM(CASE WHEN is_first_order = 1 THEN 1 ELSE 0 END) AS new_customer_orders,
        SUM(CASE WHEN is_first_order = 0 THEN 1 ELSE 0 END) AS returning_customer_orders
    FROM fact_orders
    GROUP BY order_month
)
SELECT
    m.*,
    ROUND(new_customer_revenue / revenue * 100, 1) AS new_revenue_pct,
    ROUND(returning_customer_revenue / revenue * 100, 1) AS returning_revenue_pct
FROM monthly m
ORDER BY order_month
