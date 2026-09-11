WITH base AS (
    SELECT
        user_id,
        MAX(order_ts) AS last_order,
        COUNT(*) AS frequency,
        SUM(revenue) AS monetary
    FROM orders
    WHERE delivered=1
    GROUP BY user_id
),
scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY last_order) AS recency_score,
        NTILE(5) OVER (ORDER BY frequency) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary) AS monetary_score
    FROM base
)
SELECT *,
    CASE
        WHEN frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
        WHEN frequency_score >= 3 AND monetary_score >= 3 THEN 'Loyal'
        WHEN recency_score <= 2 THEN 'At Risk'
        ELSE 'Standard'
    END AS segment
FROM scored;
