-- RFM SEGMENTATION (Recency, Frequency, Monetary)
-- classic ecommerce segmentation for targeting and personalization

DROP TABLE IF EXISTS analytics_rfm;

CREATE TABLE analytics_rfm AS
WITH rfm_raw AS (
    SELECT
        customer_id,
        full_name,
        acquisition_channel,
        -- Recency: days since last order
        CAST(julianday('now') - julianday(last_order_date) AS INTEGER) AS recency_days,
        -- Frequency: total orders
        lifetime_orders AS frequency,
        -- Monetary: total spend
        lifetime_revenue AS monetary
    FROM dim_customers
    WHERE lifetime_orders > 0
),
rfm_scored AS (
    SELECT
        *,
        -- score each dimension 1-5 (5 = best)
        -- recency: lower days = better
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- frequency: more orders = better
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        -- monetary: more spend = better
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_raw
)
SELECT
    customer_id,
    full_name,
    acquisition_channel,
    recency_days,
    frequency,
    ROUND(monetary, 2) AS monetary,
    r_score,
    f_score,
    m_score,
    r_score + f_score + m_score AS rfm_total,
    -- segment labels based on combined score
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 4 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Big Spenders Leaving'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Need Attention'
    END AS rfm_segment
FROM rfm_scored
ORDER BY rfm_total DESC
