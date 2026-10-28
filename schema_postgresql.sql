-- ============================================================
-- E-Commerce Customer Behavior Analysis
-- Phase 2 - Database Schema (PostgreSQL)
--
-- Works on PostgreSQL as-is. For SQL Server, swap:
--   SERIAL          -> INT IDENTITY(1,1)
--   NUMERIC(10,2)   -> DECIMAL(10,2)
--   TEXT            -> VARCHAR(MAX)
-- ============================================================

DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id         INTEGER PRIMARY KEY,
    name                TEXT NOT NULL,
    age                 SMALLINT NOT NULL CHECK (age BETWEEN 0 AND 120),
    gender              VARCHAR(20) NOT NULL,
    location             TEXT NOT NULL,
    registration_date   DATE NOT NULL
);

-- Derived dimension: no product master file was supplied by the
-- source system, so this holds every Product_ID referenced by
-- purchases/reviews. Extend with name/category/price columns if a
-- product catalog ever becomes available.
CREATE TABLE products (
    product_id          INTEGER PRIMARY KEY
);

CREATE TABLE purchases (
    transaction_id       INTEGER PRIMARY KEY,
    product_id           INTEGER NOT NULL REFERENCES products(product_id),
    customer_id          INTEGER NOT NULL REFERENCES customers(customer_id),
    purchase_date         DATE NOT NULL,
    quantity              SMALLINT NOT NULL CHECK (quantity > 0),
    total_price           NUMERIC(10,2) NOT NULL CHECK (total_price >= 0)
);

CREATE TABLE reviews (
    review_id             INTEGER PRIMARY KEY,
    product_id            INTEGER NOT NULL REFERENCES products(product_id),
    customer_id           INTEGER NOT NULL REFERENCES customers(customer_id),
    rating                 SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text            TEXT,
    sentiment_category     VARCHAR(10),
    text_sentiment_score   INTEGER
);

CREATE INDEX idx_purchases_customer ON purchases(customer_id);
CREATE INDEX idx_purchases_product  ON purchases(product_id);
CREATE INDEX idx_purchases_date     ON purchases(purchase_date);
CREATE INDEX idx_reviews_customer   ON reviews(customer_id);
CREATE INDEX idx_reviews_product    ON reviews(product_id);

-- ------------------------------------------------------------
-- Loading the cleaned CSVs (run from psql, adjust paths as needed)
-- ------------------------------------------------------------
-- \copy products  FROM 'cleaned_products.csv'         DELIMITER ',' CSV HEADER;
-- \copy customers FROM 'cleaned_customer_data.csv'     DELIMITER ',' CSV HEADER;
-- \copy purchases FROM 'cleaned_purchase_history.csv'  DELIMITER ',' CSV HEADER;
-- \copy reviews   FROM 'cleaned_product_reviews.csv'   DELIMITER ',' CSV HEADER;
