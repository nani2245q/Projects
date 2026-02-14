-- dimension: products with aggregated performance metrics

DROP TABLE IF EXISTS dim_products;

CREATE TABLE dim_products AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.price,
    p.compare_at_price,
    p.is_on_sale,
    p.discount_pct,
    COALESCE(ev.view_count, 0) AS total_views,
    COALESCE(ev.cart_adds, 0) AS total_cart_adds,
    COALESCE(oi.times_purchased, 0) AS total_purchases,
    COALESCE(oi.units_sold, 0) AS total_units_sold,
    COALESCE(oi.product_revenue, 0) AS total_revenue,
    -- conversion rates
    CASE WHEN COALESCE(ev.view_count, 0) > 0
        THEN ROUND(CAST(COALESCE(ev.cart_adds, 0) AS REAL) / ev.view_count * 100, 2)
        ELSE 0
    END AS view_to_cart_rate,
    CASE WHEN COALESCE(ev.cart_adds, 0) > 0
        THEN ROUND(CAST(COALESCE(oi.times_purchased, 0) AS REAL) / ev.cart_adds * 100, 2)
        ELSE 0
    END AS cart_to_purchase_rate
FROM stg_products p
LEFT JOIN (
    SELECT
        product_id,
        SUM(CASE WHEN event_type = 'product_view' THEN 1 ELSE 0 END) AS view_count,
        SUM(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS cart_adds
    FROM stg_events
    WHERE product_id IS NOT NULL
    GROUP BY product_id
) ev ON p.product_id = ev.product_id
LEFT JOIN (
    SELECT
        product_id,
        COUNT(DISTINCT order_id) AS times_purchased,
        SUM(quantity) AS units_sold,
        ROUND(SUM(line_total), 2) AS product_revenue
    FROM stg_order_items
    GROUP BY product_id
) oi ON p.product_id = oi.product_id
