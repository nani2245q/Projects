-- fact table: orders with all relevant dimensions joined

DROP TABLE IF EXISTS fact_orders;

CREATE TABLE fact_orders AS
SELECT
    o.order_id,
    o.customer_id,
    c.full_name AS customer_name,
    c.acquisition_channel AS customer_acq_channel,
    c.cohort_month AS customer_cohort,
    o.attribution_channel AS order_channel,
    o.payment_method,
    o.order_status,
    o.subtotal,
    o.tax,
    o.shipping,
    o.total,
    o.order_date_day,
    o.order_month,
    o.session_id,
    -- is this the customer's first order?
    CASE WHEN o.order_date = c.first_seen_at THEN 1
         WHEN ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date) = 1 THEN 1
         ELSE 0
    END AS is_first_order,
    -- item count
    COALESCE(items.item_count, 0) AS items_in_order,
    COALESCE(items.unique_products, 0) AS unique_products
FROM stg_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
LEFT JOIN (
    SELECT
        order_id,
        SUM(quantity) AS item_count,
        COUNT(DISTINCT product_id) AS unique_products
    FROM stg_order_items
    GROUP BY order_id
) items ON o.order_id = items.order_id
