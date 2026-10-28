import sqlite3
import pandas as pd
import os

HERE = os.path.dirname(__file__)
DB_PATH = os.path.join(HERE, "ecommerce.db")
RESULTS_DIR = os.path.join(HERE, "query_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 140)

QUERIES = {
    "01_most_purchased_products": """
        SELECT p.product_id,
               SUM(p.quantity) AS total_units_sold,
               ROUND(SUM(p.total_price), 2) AS total_revenue,
               COUNT(*) AS number_of_orders
        FROM purchases p
        GROUP BY p.product_id
        ORDER BY total_units_sold DESC
        LIMIT 10;
    """,
    "02_top_customers_by_lifetime_value": """
        SELECT c.customer_id, c.name, c.location,
               COUNT(p.transaction_id) AS number_of_orders,
               SUM(p.quantity) AS total_units_bought,
               ROUND(SUM(p.total_price), 2) AS lifetime_value
        FROM customers c
        JOIN purchases p ON p.customer_id = c.customer_id
        GROUP BY c.customer_id, c.name, c.location
        ORDER BY lifetime_value DESC
        LIMIT 10;
    """,
    "03_product_rating_summary": """
        SELECT r.product_id,
               ROUND(AVG(r.rating), 2) AS avg_rating,
               COUNT(*) AS number_of_reviews
        FROM reviews r
        GROUP BY r.product_id
        ORDER BY number_of_reviews DESC, avg_rating DESC
        LIMIT 10;
    """,
    "03b_rating_trend_by_month": """
        SELECT strftime('%Y-%m', pu.purchase_date) AS month,
               ROUND(AVG(r.rating), 2) AS avg_rating,
               COUNT(*) AS number_of_reviews
        FROM reviews r
        JOIN purchases pu
          ON pu.customer_id = r.customer_id AND pu.product_id = r.product_id
        GROUP BY month
        ORDER BY month;
    """,
    "04_regional_sales_distribution": """
        SELECT c.location,
               ROUND(SUM(p.total_price), 2) AS total_revenue,
               COUNT(*) AS number_of_orders
        FROM purchases p
        JOIN customers c ON c.customer_id = p.customer_id
        WHERE c.location <> 'Unknown'
        GROUP BY c.location
        ORDER BY total_revenue DESC
        LIMIT 15;
    """,
    "04b_unknown_location_bucket": """
        SELECT ROUND(SUM(p.total_price), 2) AS total_revenue,
               COUNT(*) AS number_of_orders
        FROM purchases p
        JOIN customers c ON c.customer_id = p.customer_id
        WHERE c.location = 'Unknown';
    """,
    "05_product_popularity_trend_by_month": """
        SELECT strftime('%Y-%m', purchase_date) AS month,
               SUM(quantity) AS units_sold,
               ROUND(SUM(total_price), 2) AS revenue
        FROM purchases
        GROUP BY month
        ORDER BY month;
    """,
    "06_sentiment_distribution": """
        SELECT sentiment_category,
               COUNT(*) AS number_of_reviews,
               ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews
        GROUP BY sentiment_category
        ORDER BY number_of_reviews DESC;
    """,
    "07_sentiment_share_top_products": """
        SELECT product_id,
               COUNT(*) AS total_reviews,
               ROUND(100.0 * SUM(CASE WHEN sentiment_category = 'Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_positive,
               ROUND(100.0 * SUM(CASE WHEN sentiment_category = 'Negative' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_negative
        FROM reviews
        GROUP BY product_id
        ORDER BY total_reviews DESC
        LIMIT 10;
    """,
    "08_age_band_spending_profile": """
        SELECT CASE
                   WHEN c.age < 25 THEN 'Under 25'
                   WHEN c.age < 35 THEN '25-34'
                   WHEN c.age < 45 THEN '35-44'
                   WHEN c.age < 55 THEN '45-54'
                   WHEN c.age < 65 THEN '55-64'
                   ELSE '65+'
               END AS age_band,
               COUNT(DISTINCT c.customer_id) AS customers,
               ROUND(SUM(p.total_price), 2) AS total_revenue,
               ROUND(AVG(p.total_price), 2) AS avg_order_value
        FROM customers c
        JOIN purchases p ON p.customer_id = c.customer_id
        GROUP BY age_band
        ORDER BY age_band;
    """,
}

for name, sql in QUERIES.items():
    df = pd.read_sql_query(sql, conn)
    df.to_csv(f"{RESULTS_DIR}/{name}.csv", index=False)
    print(f"\n=== {name} ===")
    print(df.to_string(index=False))

conn.close()
