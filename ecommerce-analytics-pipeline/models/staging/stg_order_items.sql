-- staging: order line items with revenue calc

DROP TABLE IF EXISTS stg_order_items;

CREATE TABLE stg_order_items AS
SELECT
    item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    ROUND(quantity * unit_price, 2) AS line_total
FROM raw_order_items
