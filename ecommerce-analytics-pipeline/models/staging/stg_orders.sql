-- staging: orders with calculated fields

DROP TABLE IF EXISTS stg_orders;

CREATE TABLE stg_orders AS
SELECT
    order_id,
    customer_id,
    subtotal,
    tax,
    shipping,
    total,
    LOWER(status) AS order_status,
    LOWER(payment_method) AS payment_method,
    LOWER(attribution_channel) AS attribution_channel,
    session_id,
    created_at AS order_date,
    DATE(created_at) AS order_date_day,
    strftime('%Y-%m', created_at) AS order_month,
    completed_at
FROM raw_orders
WHERE order_id IS NOT NULL
