-- staging: clean behavior events
-- normalize event types and extract date parts

DROP TABLE IF EXISTS stg_events;

CREATE TABLE stg_events AS
SELECT
    event_id,
    customer_id,
    session_id,
    LOWER(event_type) AS event_type,
    product_id,
    LOWER(attribution_channel) AS attribution_channel,
    LOWER(device_type) AS device_type,
    page_url,
    COALESCE(time_on_page, 0) AS time_on_page_seconds,
    event_timestamp,
    DATE(event_timestamp) AS event_date,
    -- extract hour for time-of-day analysis
    CAST(strftime('%H', event_timestamp) AS INTEGER) AS event_hour
FROM raw_events
WHERE event_timestamp IS NOT NULL
