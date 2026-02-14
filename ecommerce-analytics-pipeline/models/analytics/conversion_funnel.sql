-- CONVERSION FUNNEL ANALYSIS
-- track drop-off at each stage of the purchase journey

DROP TABLE IF EXISTS analytics_funnel;

CREATE TABLE analytics_funnel AS
WITH funnel_counts AS (
    SELECT
        'page_view' AS stage,
        1 AS stage_order,
        COUNT(DISTINCT customer_id) AS unique_users,
        COUNT(DISTINCT session_id) AS unique_sessions
    FROM stg_events WHERE event_type = 'page_view'

    UNION ALL

    SELECT 'product_view', 2,
        COUNT(DISTINCT customer_id),
        COUNT(DISTINCT session_id)
    FROM stg_events WHERE event_type = 'product_view'

    UNION ALL

    SELECT 'add_to_cart', 3,
        COUNT(DISTINCT customer_id),
        COUNT(DISTINCT session_id)
    FROM stg_events WHERE event_type = 'add_to_cart'

    UNION ALL

    SELECT 'checkout_start', 4,
        COUNT(DISTINCT customer_id),
        COUNT(DISTINCT session_id)
    FROM stg_events WHERE event_type = 'checkout_start'

    UNION ALL

    SELECT 'checkout_complete', 5,
        COUNT(DISTINCT customer_id),
        COUNT(DISTINCT session_id)
    FROM stg_events WHERE event_type = 'checkout_complete'
)
SELECT
    stage,
    stage_order,
    unique_users,
    unique_sessions,
    -- drop-off from first stage
    ROUND(
        CAST(unique_users AS REAL) /
        (SELECT unique_users FROM funnel_counts WHERE stage_order = 1) * 100, 2
    ) AS pct_of_total,
    -- drop-off from previous stage (calculated in Python since SQLite
    -- doesn't have LAG without a workaround)
    unique_users AS users_at_stage
FROM funnel_counts
ORDER BY stage_order
