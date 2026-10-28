-- SQLite version of the schema (same structure as schema_postgresql.sql),
-- used here to actually build and query a working database, since a
-- standalone PostgreSQL/SQL Server instance isn't available in this
-- environment. The DDL and queries are near-identical between engines.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id         INTEGER PRIMARY KEY,
    name                 TEXT NOT NULL,
    age                   INTEGER NOT NULL CHECK (age BETWEEN 0 AND 120),
    gender                 TEXT NOT NULL,
    location                TEXT NOT NULL,
    registration_date       DATE NOT NULL
);

CREATE TABLE products (
    product_id            INTEGER PRIMARY KEY
);

CREATE TABLE purchases (
    transaction_id         INTEGER PRIMARY KEY,
    product_id              INTEGER NOT NULL REFERENCES products(product_id),
    customer_id              INTEGER NOT NULL REFERENCES customers(customer_id),
    purchase_date              DATE NOT NULL,
    quantity                    INTEGER NOT NULL CHECK (quantity > 0),
    total_price                  REAL NOT NULL CHECK (total_price >= 0)
);

CREATE TABLE reviews (
    review_id               INTEGER PRIMARY KEY,
    product_id                INTEGER NOT NULL REFERENCES products(product_id),
    customer_id                 INTEGER NOT NULL REFERENCES customers(customer_id),
    rating                        INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text                    TEXT,
    sentiment_category               TEXT,
    text_sentiment_score               INTEGER
);

CREATE INDEX idx_purchases_customer ON purchases(customer_id);
CREATE INDEX idx_purchases_product  ON purchases(product_id);
CREATE INDEX idx_purchases_date     ON purchases(purchase_date);
CREATE INDEX idx_reviews_customer   ON reviews(customer_id);
CREATE INDEX idx_reviews_product    ON reviews(product_id);
