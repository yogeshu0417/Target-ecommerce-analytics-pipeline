"""
E-Commerce Customer Behavior Analysis
Phase 2 - build a working database from the cleaned CSVs.

Uses SQLite so the database is a single portable file that runs
anywhere with no server setup. The schema (schema_sqlite.sql) mirrors
schema_postgresql.sql, so the same tables/queries carry over directly
to a real PostgreSQL/SQL Server instance for production use.
"""

import sqlite3
import pandas as pd
import os

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "..", "data")
DB_PATH = os.path.join(HERE, "ecommerce.db")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
with open(os.path.join(HERE, "schema_sqlite.sql")) as f:
    conn.executescript(f.read())

products = pd.read_csv(f"{DATA_DIR}/cleaned_products.csv")
customers = pd.read_csv(f"{DATA_DIR}/cleaned_customer_data.csv")
purchases = pd.read_csv(f"{DATA_DIR}/cleaned_purchase_history.csv")
reviews = pd.read_csv(f"{DATA_DIR}/cleaned_product_reviews.csv")

products.to_sql("products", conn, if_exists="append", index=False)
customers.rename(columns={
    "Customer_ID": "customer_id", "Name": "name", "Age": "age",
    "Gender": "gender", "Location": "location", "Registration_Date": "registration_date"
}).to_sql("customers", conn, if_exists="append", index=False)
purchases.rename(columns={
    "Transaction_ID": "transaction_id", "Product_ID": "product_id", "Customer_ID": "customer_id",
    "Purchase_Date": "purchase_date", "Quantity": "quantity", "Total_Price": "total_price"
}).to_sql("purchases", conn, if_exists="append", index=False)
reviews.rename(columns={
    "Review_ID": "review_id", "Product_ID": "product_id", "Customer_ID": "customer_id",
    "Rating": "rating", "Review_Text": "review_text",
    "Sentiment_Category": "sentiment_category", "Text_Sentiment_Score": "text_sentiment_score"
}).to_sql("reviews", conn, if_exists="append", index=False)

conn.commit()

for t in ["customers", "products", "purchases", "reviews"]:
    n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t}: {n} rows loaded")

conn.close()
print(f"\nDatabase written to {DB_PATH}")
