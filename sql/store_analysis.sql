
-- DMart Regional Analytics
-- SQLite queries using the cleaned daily store dataset.
-- Table required: store_daily_clean

-- Q1: Average daily revenue by store
SELECT
    store,
    ROUND(AVG(revenue_inr), 2) AS avg_daily_revenue
FROM store_daily_clean
GROUP BY store
ORDER BY avg_daily_revenue DESC;

-- Q2: Average target achievement by store
SELECT
    store,
    ROUND(AVG(achievement_pct), 2) AS avg_achievement_pct
FROM store_daily_clean
GROUP BY store
ORDER BY avg_achievement_pct DESC;

-- Q3: Average stockout hours by store
SELECT
    store,
    ROUND(AVG(stockout_hours), 2) AS avg_stockout_hours
FROM store_daily_clean
GROUP BY store
ORDER BY avg_stockout_hours DESC;

-- Q4: Average customer footfall by store
SELECT
    store,
    ROUND(AVG(footfall), 2) AS avg_footfall
FROM store_daily_clean
GROUP BY store
ORDER BY avg_footfall DESC;

-- Q5: Days when stores missed their targets
SELECT
    store,
    COUNT(*) AS days_below_target
FROM store_daily_clean
WHERE revenue_inr < daily_target_inr
GROUP BY store
ORDER BY days_below_target DESC;

-- Q6: Monthly revenue by store
SELECT
    store,
    SUBSTR(date, 1, 7) AS month,
    ROUND(SUM(revenue_inr), 2) AS monthly_revenue
FROM store_daily_clean
GROUP BY store, SUBSTR(date, 1, 7)
ORDER BY store, month;
