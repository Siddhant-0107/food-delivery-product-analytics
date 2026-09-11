SELECT
    COUNT(*) AS orders,
    SUM(delivered) AS delivered_orders,
    ROUND(100.0 * AVG(delivered), 2) AS delivery_rate_pct,
    ROUND(100.0 * AVG(cancelled), 2) AS cancellation_rate_pct,
    ROUND(AVG(eta_minutes), 2) AS avg_eta_minutes,
    ROUND(AVG(CASE WHEN delivered=1 THEN revenue ELSE 0 END), 2) AS revenue_per_order,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM orders;
