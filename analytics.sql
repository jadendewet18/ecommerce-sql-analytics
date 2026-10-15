-- ==========================================================
-- E-COMMERCE ANALYTICS & RFM SEGMENTATION QUERIES
-- ==========================================================

-- QUERY 1: RFM Customer Segmentation
-- Segments customers into Champions, Loyal, At-Risk, or Standard based on:
-- Recency (Days since last purchase), Frequency (Total orders), and Monetary (Total spend)
WITH customer_totals AS (
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        MAX(o.order_date) AS last_order_date,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.quantity * oi.unit_price) AS total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Completed'
    GROUP BY c.customer_id, customer_name
),
rfm_scores AS (
    SELECT 
        customer_id,
        customer_name,
        total_orders,
        total_spent,
        -- Calculate days since last order relative to a fixed cutoff date
        JULIANDAY('2026-06-30') - JULIANDAY(last_order_date) AS recency_days,
        NTILE(4) OVER (ORDER BY JULIANDAY('2026-06-30') - JULIANDAY(last_order_date) DESC) AS r_score,
        NTILE(4) OVER (ORDER BY total_orders ASC) AS f_score,
        NTILE(4) OVER (ORDER BY total_spent ASC) AS m_score
    FROM customer_totals
)
SELECT 
    customer_id,
    customer_name,
    ROUND(recency_days, 0) AS recency_days,
    total_orders,
    ROUND(total_spent, 2) AS total_spent,
    CASE 
        WHEN r_score = 4 AND f_score = 4 AND m_score = 4 THEN 'VIP / Champion'
        WHEN f_score >= 3 AND r_score >= 3 THEN 'Loyal Customer'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At-Risk / Needs Attention'
        ELSE 'Standard Customer'
    END AS customer_segment
FROM rfm_scores
ORDER BY total_spent DESC;


-- QUERY 2: Month-over-Month (MoM) Revenue & Growth
-- Calculates monthly revenues and tracks growth percentages using the LAG() window function
WITH monthly_revenue AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_date) AS sales_month,
        SUM(oi.quantity * oi.unit_price) AS current_month_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Completed'
    GROUP BY sales_month
)
SELECT 
    sales_month,
    ROUND(current_month_revenue, 2) AS revenue,
    ROUND(LAG(current_month_revenue, 1) OVER (ORDER BY sales_month), 2) AS previous_month_revenue,
    ROUND(
        (current_month_revenue - LAG(current_month_revenue, 1) OVER (ORDER BY sales_month)) 
        / LAG(current_month_revenue, 1) OVER (ORDER BY sales_month) * 100, 2
    ) AS mom_growth_percentage
FROM monthly_revenue;