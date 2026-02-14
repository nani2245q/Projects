-- dimension: date spine for joining time-based analyses
-- generates every day in the data range

DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date AS
WITH RECURSIVE dates(d) AS (
    SELECT DATE(MIN(event_timestamp)) FROM raw_events
    UNION ALL
    SELECT DATE(d, '+1 day') FROM dates
    WHERE d < DATE('now')
)
SELECT
    d AS date_day,
    strftime('%Y-%m', d) AS year_month,
    strftime('%Y', d) AS year,
    CAST(strftime('%m', d) AS INTEGER) AS month_num,
    CASE CAST(strftime('%m', d) AS INTEGER)
        WHEN 1 THEN 'Jan' WHEN 2 THEN 'Feb' WHEN 3 THEN 'Mar'
        WHEN 4 THEN 'Apr' WHEN 5 THEN 'May' WHEN 6 THEN 'Jun'
        WHEN 7 THEN 'Jul' WHEN 8 THEN 'Aug' WHEN 9 THEN 'Sep'
        WHEN 10 THEN 'Oct' WHEN 11 THEN 'Nov' WHEN 12 THEN 'Dec'
    END AS month_name,
    CAST(strftime('%W', d) AS INTEGER) AS week_of_year,
    CASE CAST(strftime('%w', d) AS INTEGER)
        WHEN 0 THEN 'Sun' WHEN 1 THEN 'Mon' WHEN 2 THEN 'Tue'
        WHEN 3 THEN 'Wed' WHEN 4 THEN 'Thu' WHEN 5 THEN 'Fri'
        WHEN 6 THEN 'Sat'
    END AS day_of_week,
    CASE WHEN CAST(strftime('%w', d) AS INTEGER) IN (0, 6) THEN 1 ELSE 0 END AS is_weekend
FROM dates
