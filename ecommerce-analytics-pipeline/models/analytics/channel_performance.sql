-- CHANNEL PERFORMANCE by device type
-- cross-tab of channel x device for understanding where to invest

DROP TABLE IF EXISTS analytics_channel_device;

CREATE TABLE analytics_channel_device AS
SELECT
    s.attribution_channel AS channel,
    s.device_type,
    COUNT(DISTINCT s.session_id) AS sessions,
    SUM(s.product_views) AS product_views,
    SUM(s.completed_checkout) AS purchases,
    ROUND(
        CAST(SUM(s.completed_checkout) AS REAL) / COUNT(DISTINCT s.session_id) * 100, 2
    ) AS conversion_rate,
    ROUND(AVG(s.total_time_on_site), 1) AS avg_time_on_site,
    ROUND(AVG(s.total_events), 1) AS avg_events_per_session
FROM fact_sessions s
GROUP BY s.attribution_channel, s.device_type
ORDER BY channel, device_type
