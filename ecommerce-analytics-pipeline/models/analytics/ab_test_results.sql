-- A/B TEST RESULTS
-- aggregate conversion metrics per test per variant for statistical comparison

DROP TABLE IF EXISTS analytics_ab_test_results;

CREATE TABLE analytics_ab_test_results AS
SELECT
    t.test_id,
    t.test_name,
    t.description,
    t.metric,
    t.status,
    t.start_date,
    t.end_date,
    a.variant,
    COUNT(*) AS sample_size,
    SUM(a.converted) AS conversions,
    ROUND(CAST(SUM(a.converted) AS REAL) / COUNT(*) * 100, 2) AS conversion_rate,
    ROUND(AVG(CASE WHEN a.converted = 1 THEN a.conversion_value END), 2) AS avg_conversion_value,
    ROUND(SUM(a.conversion_value), 2) AS total_value
FROM raw_ab_tests t
JOIN raw_ab_assignments a ON t.test_id = a.test_id
GROUP BY t.test_id, t.test_name, t.description, t.metric, t.status,
         t.start_date, t.end_date, a.variant
ORDER BY t.test_id, a.variant
