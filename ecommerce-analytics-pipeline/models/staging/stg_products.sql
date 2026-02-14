-- staging: products with discount flag

DROP TABLE IF EXISTS stg_products;

CREATE TABLE stg_products AS
SELECT
    product_id,
    name AS product_name,
    LOWER(category) AS category,
    price,
    compare_at_price,
    CASE
        WHEN compare_at_price IS NOT NULL AND compare_at_price > price
        THEN 1 ELSE 0
    END AS is_on_sale,
    CASE
        WHEN compare_at_price IS NOT NULL AND compare_at_price > price
        THEN ROUND((compare_at_price - price) / compare_at_price * 100, 1)
        ELSE 0
    END AS discount_pct,
    created_at
FROM raw_products
