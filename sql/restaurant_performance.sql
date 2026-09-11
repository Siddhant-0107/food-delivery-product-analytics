SELECT
    r.restaurant_id,
    r.cuisine,
    ROUND(r.rating,2) AS rating,
    COUNT(o.order_id) AS orders,
    ROUND(AVG(o.eta_minutes),2) AS avg_eta,
    ROUND(100.0*AVG(o.cancelled),2) AS cancellation_pct,
    ROUND(SUM(o.revenue),2) AS revenue
FROM restaurants r
JOIN orders o USING (restaurant_id)
GROUP BY 1,2,3
ORDER BY revenue DESC;
