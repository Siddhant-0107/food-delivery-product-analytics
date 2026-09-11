-- Product Analytics Query Pack
-- Adapt table/column names if the generated schema changes.

-- 1. Daily core KPI trend
SELECT
    DATE(order_timestamp) AS order_date,
    COUNT(*) AS orders,
    SUM(order_value) AS gmv,
    AVG(order_value) AS aov,
    AVG(CASE WHEN status = 'cancelled' THEN 1.0 ELSE 0.0 END) AS cancellation_rate
FROM orders
GROUP BY 1
ORDER BY 1;

-- 2. Returning customer rate
WITH customer_orders AS (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    WHERE status <> 'cancelled'
    GROUP BY customer_id
)
SELECT
    AVG(CASE WHEN order_count >= 2 THEN 1.0 ELSE 0.0 END) AS repeat_customer_rate
FROM customer_orders;

-- 3. Restaurant scorecard
SELECT
    restaurant_id,
    COUNT(*) AS orders,
    AVG(CASE WHEN status <> 'cancelled' THEN 1.0 ELSE 0.0 END) AS completion_rate,
    AVG(CASE WHEN delivery_minutes <= promised_minutes THEN 1.0 ELSE 0.0 END) AS sla_rate,
    AVG(delivery_minutes) AS avg_delivery_minutes
FROM orders
GROUP BY restaurant_id
ORDER BY orders DESC;

-- 4. Peak-hour demand
SELECT
    EXTRACT(HOUR FROM order_timestamp) AS order_hour,
    COUNT(*) AS orders,
    AVG(order_value) AS aov
FROM orders
WHERE status <> 'cancelled'
GROUP BY 1
ORDER BY 1;

-- 5. Cohort retention concept
-- Define each customer's first completed-order month,
-- then measure subsequent active months.
WITH first_order AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_timestamp)) AS cohort_month
    FROM orders
    WHERE status <> 'cancelled'
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT
        o.customer_id,
        f.cohort_month,
        DATE_TRUNC('month', o.order_timestamp) AS activity_month
    FROM orders o
    JOIN first_order f USING (customer_id)
    WHERE o.status <> 'cancelled'
)
SELECT
    cohort_month,
    activity_month,
    COUNT(DISTINCT customer_id) AS retained_customers
FROM activity
GROUP BY 1, 2
ORDER BY 1, 2;
