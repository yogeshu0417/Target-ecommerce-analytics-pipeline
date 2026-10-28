-- ============================================================
-- E-Commerce Customer Behavior Analysis
-- Phase 2 - Analysis Queries
-- Standard ANSI SQL; runs unchanged on PostgreSQL, SQL Server and
-- SQLite (the only engine-specific bit is date-part extraction,
-- noted where it's used).
-- ============================================================

-- 1. MOST PURCHASED PRODUCTS (by total quantity sold, then revenue)
SELECT
    p.product_id,
    SUM(p.quantity)      AS total_units_sold,
    ROUND(SUM(p.total_price), 2) AS total_revenue,
    COUNT(*)             AS number_of_orders
FROM purchases p
GROUP BY p.product_id
ORDER BY total_units_sold DESC
LIMIT 10;


-- 2. TOP CUSTOMERS BY LIFETIME VALUE (total amount spent)
SELECT
    c.customer_id,
    c.name,
    c.location,
    COUNT(p.transaction_id)      AS number_of_orders,
    SUM(p.quantity)              AS total_units_bought,
    ROUND(SUM(p.total_price), 2) AS lifetime_value
FROM customers c
JOIN purchases p ON p.customer_id = c.customer_id
GROUP BY c.customer_id, c.name, c.location
ORDER BY lifetime_value DESC
LIMIT 10;


-- 3. PRODUCT RATING TRENDS OVER TIME
-- (avg rating per product per month, using the review's own timeline
--  is not available -- reviews have no date column in the source data,
--  so this version trends by product across all reviews; see the
--  purchase-month version below for a genuine time trend.)
SELECT
    r.product_id,
    ROUND(AVG(r.rating), 2) AS avg_rating,
    COUNT(*)                AS number_of_reviews
FROM reviews r
GROUP BY r.product_id
ORDER BY number_of_reviews DESC, avg_rating DESC
LIMIT 10;

-- 3b. Rating trend by month, using the associated purchase date as the
--     time axis (join reviews to purchases on customer+product).
--     SQLite: strftime('%Y-%m', ...); PostgreSQL: to_char(..., 'YYYY-MM')
SELECT
    strftime('%Y-%m', pu.purchase_date) AS month,
    ROUND(AVG(r.rating), 2)             AS avg_rating,
    COUNT(*)                            AS number_of_reviews
FROM reviews r
JOIN purchases pu
  ON pu.customer_id = r.customer_id AND pu.product_id = r.product_id
GROUP BY month
ORDER BY month;


-- ============================================================
-- Supporting queries for the Phase 3 Power BI dashboards
-- ============================================================

-- 4. REGIONAL SALES DISTRIBUTION (revenue by customer location)
-- 'Unknown' (customers whose Location was missing in the source data
-- and was standardized during cleaning) is excluded here so it doesn't
-- get mistaken for a real top-performing region; see query 4b for its size.
SELECT
    c.location,
    ROUND(SUM(p.total_price), 2) AS total_revenue,
    COUNT(*)                     AS number_of_orders
FROM purchases p
JOIN customers c ON c.customer_id = p.customer_id
WHERE c.location <> 'Unknown'
GROUP BY c.location
ORDER BY total_revenue DESC
LIMIT 15;

-- 4b. Size of the 'Unknown' location bucket (data-quality check)
SELECT
    ROUND(SUM(p.total_price), 2) AS total_revenue,
    COUNT(*)                     AS number_of_orders
FROM purchases p
JOIN customers c ON c.customer_id = p.customer_id
WHERE c.location = 'Unknown';

-- 5. PRODUCT POPULARITY TREND OVER TIME (units sold by month)
SELECT
    strftime('%Y-%m', purchase_date) AS month,
    SUM(quantity)                    AS units_sold,
    ROUND(SUM(total_price), 2)       AS revenue
FROM purchases
GROUP BY month
ORDER BY month;

-- 6. CUSTOMER SENTIMENT ANALYSIS FROM REVIEWS (distribution)
SELECT
    sentiment_category,
    COUNT(*)                 AS number_of_reviews,
    ROUND(AVG(rating), 2)    AS avg_rating
FROM reviews
GROUP BY sentiment_category
ORDER BY number_of_reviews DESC;

-- 7. SENTIMENT SHARE PER PRODUCT (top 10 most-reviewed products)
SELECT
    product_id,
    COUNT(*) AS total_reviews,
    ROUND(100.0 * SUM(CASE WHEN sentiment_category = 'Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_positive,
    ROUND(100.0 * SUM(CASE WHEN sentiment_category = 'Negative' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_negative
FROM reviews
GROUP BY product_id
ORDER BY total_reviews DESC
LIMIT 10;

-- 8. AGE-BAND SPENDING PROFILE (useful cut for the customer dashboard)
SELECT
    CASE
        WHEN c.age < 25 THEN 'Under 25'
        WHEN c.age < 35 THEN '25-34'
        WHEN c.age < 45 THEN '35-44'
        WHEN c.age < 55 THEN '45-54'
        WHEN c.age < 65 THEN '55-64'
        ELSE '65+'
    END AS age_band,
    COUNT(DISTINCT c.customer_id) AS customers,
    ROUND(SUM(p.total_price), 2)  AS total_revenue,
    ROUND(AVG(p.total_price), 2)  AS avg_order_value
FROM customers c
JOIN purchases p ON p.customer_id = c.customer_id
GROUP BY age_band
ORDER BY age_band;
