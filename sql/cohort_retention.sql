WITH first_order AS (
    SELECT user_id, DATE_TRUNC('month', MIN(order_ts)) AS cohort_month
    FROM orders WHERE delivered=1 GROUP BY user_id
),
activity AS (
    SELECT DISTINCT user_id, DATE_TRUNC('month', order_ts) AS activity_month
    FROM orders WHERE delivered=1
)
SELECT
    f.cohort_month,
    DATE_DIFF('month', f.cohort_month, a.activity_month) AS month_number,
    COUNT(DISTINCT a.user_id) AS active_users
FROM first_order f
JOIN activity a USING(user_id)
GROUP BY 1,2
ORDER BY 1,2;
