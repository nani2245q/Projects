-- MARKETING ATTRIBUTION ANALYSIS
-- which channels drive revenue vs just traffic?
-- this is basically what Chord's Context Graph captures

DROP TABLE IF EXISTS analytics_attribution;

CREATE TABLE analytics_attribution AS
SELECT
    s.attribution_channel AS channel,
    COUNT(DISTINCT s.session_id) AS total_sessions,
    COUNT(DISTINCT s.customer_id) AS unique_visitors,
    SUM(s.product_views) AS total_product_views,
    SUM(s.cart_adds) AS total_cart_adds,
    SUM(s.completed_checkout) AS conversions,
    -- conversion rate: sessions that led to a purchase
    ROUND(
        CAST(SUM(s.completed_checkout) AS REAL) / COUNT(DISTINCT s.session_id) * 100, 2
    ) AS conversion_rate,
    -- revenue from this channel
    COALESCE(rev.channel_revenue, 0) AS total_revenue,
    COALESCE(rev.channel_orders, 0) AS total_orders,
    -- revenue per session (key efficiency metric)
    ROUND(
        COALESCE(rev.channel_revenue, 0) / CAST(COUNT(DISTINCT s.session_id) AS REAL), 2
    ) AS revenue_per_session,
    -- avg order value by channel
    CASE WHEN COALESCE(rev.channel_orders, 0) > 0
        THEN ROUND(rev.channel_revenue / rev.channel_orders, 2)
        ELSE 0
    END AS avg_order_value,
    -- % of total revenue
    ROUND(
        COALESCE(rev.channel_revenue, 0) /
        (SELECT SUM(total) FROM fact_orders) * 100, 2
    ) AS revenue_share_pct
FROM fact_sessions s
LEFT JOIN (
    SELECT
        order_channel,
        SUM(total) AS channel_revenue,
        COUNT(*) AS channel_orders
    FROM fact_orders
    GROUP BY order_channel
) rev ON s.attribution_channel = rev.order_channel
GROUP BY s.attribution_channel
ORDER BY total_revenue DESC
