-- fact table: sessions aggregated from events
-- each row = one user session with metrics

DROP TABLE IF EXISTS fact_sessions;

CREATE TABLE fact_sessions AS
SELECT
    e.session_id,
    e.customer_id,
    e.attribution_channel,
    e.device_type,
    MIN(e.event_timestamp) AS session_start,
    MAX(e.event_timestamp) AS session_end,
    DATE(MIN(e.event_timestamp)) AS session_date,
    COUNT(*) AS total_events,
    SUM(CASE WHEN e.event_type = 'page_view' THEN 1 ELSE 0 END) AS page_views,
    SUM(CASE WHEN e.event_type = 'product_view' THEN 1 ELSE 0 END) AS product_views,
    SUM(CASE WHEN e.event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS cart_adds,
    MAX(CASE WHEN e.event_type = 'checkout_start' THEN 1 ELSE 0 END) AS started_checkout,
    MAX(CASE WHEN e.event_type = 'checkout_complete' THEN 1 ELSE 0 END) AS completed_checkout,
    MAX(CASE WHEN e.event_type = 'checkout_abandon' THEN 1 ELSE 0 END) AS abandoned_checkout,
    SUM(e.time_on_page_seconds) AS total_time_on_site
FROM stg_events e
GROUP BY e.session_id, e.customer_id, e.attribution_channel, e.device_type
