-- Product Analytics Query Pack
-- Schema used by this project: orders(order_id, user_id, restaurant_id, order_ts,
-- traffic, weather, eta_minutes, cancelled, delivered, revenue, ...)

-- 1. Daily core KPI trend
SELECT
    DATE_TRUNC('day', order_ts) AS order_date,
    COUNT(*) AS orders,
    SUM(CASE WHEN delivered = 1 THEN revenue ELSE 0 END) AS gmv,
    AVG(CASE WHEN delivered = 1 THEN revenue END) AS aov,
    AVG(cancelled) * 100 AS cancellation_rate_pct,
    AVG(delivered) * 100 AS delivery_rate_pct,
    AVG(CASE WHEN delivered = 1 AND eta_minutes <= 45 THEN 1.0 ELSE 0.0 END) * 100 AS sla_45_pct
FROM orders
GROUP BY 1
ORDER BY 1;

-- 2. Returning customer rate
WITH customer_orders AS (
    SELECT
        user_id,
        COUNT(*) AS order_count
    FROM orders
    WHERE delivered = 1
    GROUP BY user_id
)
SELECT
    AVG(CASE WHEN order_count >= 2 THEN 1.0 ELSE 0.0 END) * 100 AS repeat_customer_rate_pct
FROM customer_orders;

-- 3. Restaurant scorecard
SELECT
    restaurant_id,
    COUNT(*) AS orders,
    SUM(CASE WHEN delivered = 1 THEN revenue ELSE 0 END) AS gmv,
    AVG(CASE WHEN delivered = 1 THEN 1.0 ELSE 0.0 END) * 100 AS delivery_rate_pct,
    AVG(CASE WHEN delivered = 1 AND eta_minutes <= 45 THEN 1.0 ELSE 0.0 END) * 100 AS sla_45_pct,
    AVG(eta_minutes) AS avg_eta_minutes,
    AVG(cancelled) * 100 AS cancellation_rate_pct
FROM orders
GROUP BY restaurant_id
ORDER BY gmv DESC;

-- 4. Peak-hour demand
SELECT
    EXTRACT(HOUR FROM order_ts) AS order_hour,
    COUNT(*) AS orders,
    AVG(CASE WHEN delivered = 1 THEN revenue END) AS aov
FROM orders
GROUP BY 1
ORDER BY orders DESC;

-- 5. Cohort retention concept
-- Define each customer's first completed-order month,
-- then measure subsequent active months.
WITH first_order AS (
    SELECT
        user_id,
        DATE_TRUNC('month', MIN(order_ts)) AS cohort_month
    FROM orders
    WHERE delivered = 1
    GROUP BY user_id
),
activity AS (
    SELECT DISTINCT
        o.user_id,
        f.cohort_month,
        DATE_TRUNC('month', o.order_ts) AS activity_month
    FROM orders o
    JOIN first_order f USING (user_id)
    WHERE o.delivered = 1
)
SELECT
    cohort_month,
    DATE_DIFF('month', cohort_month, activity_month) AS month_number,
    COUNT(DISTINCT user_id) AS retained_customers
FROM activity
GROUP BY 1, 2
ORDER BY 1, 2;

-- 6. Rolling 7-day orders
WITH daily AS (
    SELECT
        DATE_TRUNC('day', order_ts) AS order_date,
        COUNT(*) AS orders
    FROM orders
    GROUP BY 1
)
SELECT
    order_date,
    orders,
    AVG(orders) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_orders
FROM daily
ORDER BY order_date;

-- 7. Top 3 restaurants within each cuisine
WITH restaurant_gmv AS (
    SELECT
        r.cuisine,
        o.restaurant_id,
        SUM(CASE WHEN o.delivered = 1 THEN o.revenue ELSE 0 END) AS gmv
    FROM orders o
    JOIN restaurants r USING (restaurant_id)
    GROUP BY 1, 2
), ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY cuisine ORDER BY gmv DESC) AS rn
    FROM restaurant_gmv
)
SELECT *
FROM ranked
WHERE rn <= 3
ORDER BY cuisine, rn;
