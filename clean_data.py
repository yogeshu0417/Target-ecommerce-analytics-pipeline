"""
E-Commerce Customer Behavior Analysis
Phase 1 - Data Cleaning & Preprocessing (Python / Pandas)

Reads the three raw source files, cleans them, and writes cleaned CSVs
ready for Phase 2 (SQL) and Phase 3 (Power BI).

Run:  python clean_data.py
"""

import pandas as pd
import numpy as np
import os

RAW_DIR = "/mnt/user-data/uploads"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT_DIR, exist_ok=True)

log = []  # data-quality log entries printed at the end


def note(msg):
    print(msg)
    log.append(msg)


# A small built-in lexicon so we can score review text without any
# internet-dependent NLP package (network access in this environment
# is restricted). Good enough for a demo/training project; a real
# deployment would swap this for TextBlob/VADER/a transformer model.
POSITIVE_WORDS = {
    "good", "great", "excellent", "love", "amazing", "happy", "best",
    "wonderful", "perfect", "nice", "fantastic", "recommend", "easy",
    "helpful", "friendly", "quality", "fast", "safe",
}
NEGATIVE_WORDS = {
    "bad", "poor", "terrible", "hate", "worst", "awful", "difficult",
    "slow", "problem", "broken", "disappoint", "wrong", "hard", "attack",
}


def text_sentiment_score(text):
    if not isinstance(text, str) or not text.strip():
        return 0
    words = set(w.strip(".,!?").lower() for w in text.split())
    return len(words & POSITIVE_WORDS) - len(words & NEGATIVE_WORDS)


# ---------------------------------------------------------------------------
# 1. LOAD
# ---------------------------------------------------------------------------
customers = pd.read_csv(f"{RAW_DIR}/ecommerce_customer_data.csv")
purchases = pd.read_csv(f"{RAW_DIR}/ecommerce_purchase_history.csv")
reviews = pd.read_csv(f"{RAW_DIR}/ecommerce_product_reviews.csv")

note("RAW SHAPES")
note(f"  customers: {customers.shape}   purchases: {purchases.shape}   reviews: {reviews.shape}")

# ---------------------------------------------------------------------------
# 2. REMOVE EXACT DUPLICATE ROWS
# ---------------------------------------------------------------------------
for name, df in [("customers", customers), ("purchases", purchases), ("reviews", reviews)]:
    before = len(df)
    df.drop_duplicates(inplace=True)
    note(f"[{name}] removed {before - len(df)} exact duplicate rows -> {len(df)} rows left")

# ---------------------------------------------------------------------------
# 3. CUSTOMERS: types, missing values
# ---------------------------------------------------------------------------
note("\nCLEANING customers")
before = len(customers)
customers = customers.dropna(subset=["Customer_ID"])
note(f"  dropped {before - len(customers)} rows with missing Customer_ID (no way to identify the customer)")

customers["Customer_ID"] = customers["Customer_ID"].astype("int64")

age_median = customers["Age"].median()
n_missing_age = customers["Age"].isnull().sum()
customers["Age"] = customers["Age"].fillna(age_median).astype("int64")
note(f"  imputed {n_missing_age} missing Age values with the median age ({age_median:.0f})")

gender_mode = customers["Gender"].mode()[0]
n_missing_gender = customers["Gender"].isnull().sum()
customers["Gender"] = customers["Gender"].fillna(gender_mode)
note(f"  imputed {n_missing_gender} missing Gender values with the most common category ('{gender_mode}')")

n_missing_loc = customers["Location"].isnull().sum()
customers["Location"] = customers["Location"].fillna("Unknown")
note(f"  filled {n_missing_loc} missing Location values with 'Unknown' "
     f"(Location is high-cardinality/near-unique per customer, so mode imputation would "
     f"misleadingly cluster them into one arbitrary city)")

n_missing_name = customers["Name"].isnull().sum()
customers["Name"] = customers["Name"].fillna("Unknown")
note(f"  filled {n_missing_name} missing Name values with 'Unknown'")

customers["Registration_Date"] = pd.to_datetime(customers["Registration_Date"], errors="coerce")
before = len(customers)
customers = customers.dropna(subset=["Registration_Date"])
note(f"  dropped {before - len(customers)} rows with missing/unparseable Registration_Date "
     f"(a fabricated signup date would distort tenure & cohort analysis)")

customers = customers.drop_duplicates(subset=["Customer_ID"], keep="first")
note(f"  customers final shape: {customers.shape}")

# ---------------------------------------------------------------------------
# 4. PURCHASES: types, missing values, referential integrity
# ---------------------------------------------------------------------------
note("\nCLEANING purchases")
before = len(purchases)
purchases = purchases.dropna(subset=["Transaction_ID"])
note(f"  dropped {before - len(purchases)} rows with missing Transaction_ID")

before = len(purchases)
purchases = purchases.dropna(subset=["Customer_ID", "Product_ID"])
note(f"  dropped {before - len(purchases)} rows with missing Customer_ID or Product_ID "
     f"(a transaction needs to know who bought what)")

purchases["Purchase_Date"] = pd.to_datetime(purchases["Purchase_Date"], errors="coerce")
before = len(purchases)
purchases = purchases.dropna(subset=["Purchase_Date"])
note(f"  dropped {before - len(purchases)} rows with missing/unparseable Purchase_Date")

qty_median = purchases["Quantity"].median()
n_missing_qty = purchases["Quantity"].isnull().sum()
purchases["Quantity"] = purchases["Quantity"].fillna(qty_median)
note(f"  imputed {n_missing_qty} missing Quantity values with the median quantity ({qty_median:.0f})")

# Impute missing Total_Price from the median *unit price* of the same
# product where possible (more accurate than a flat global median),
# falling back to the global median Total_Price otherwise.
purchases["Unit_Price_tmp"] = purchases["Total_Price"] / purchases["Quantity"]
product_unit_price = purchases.groupby("Product_ID")["Unit_Price_tmp"].median()
global_price_median = purchases["Total_Price"].median()

n_missing_price = purchases["Total_Price"].isnull().sum()
mask = purchases["Total_Price"].isnull()
est_from_product = purchases.loc[mask, "Product_ID"].map(product_unit_price) * purchases.loc[mask, "Quantity"]
purchases.loc[mask, "Total_Price"] = est_from_product
purchases["Total_Price"] = purchases["Total_Price"].fillna(global_price_median)
purchases.drop(columns=["Unit_Price_tmp"], inplace=True)
note(f"  imputed {n_missing_price} missing Total_Price values "
     f"(product-level median unit price x quantity, falling back to the global median price)")

purchases["Total_Price"] = purchases["Total_Price"].round(2)
purchases["Transaction_ID"] = purchases["Transaction_ID"].astype("int64")
purchases["Product_ID"] = purchases["Product_ID"].astype("int64")
purchases["Customer_ID"] = purchases["Customer_ID"].astype("int64")
purchases["Quantity"] = purchases["Quantity"].astype("int64")

purchases = purchases.drop_duplicates(subset=["Transaction_ID"], keep="first")

before = len(purchases)
purchases = purchases[purchases["Customer_ID"].isin(customers["Customer_ID"])]
note(f"  dropped {before - len(purchases)} rows whose Customer_ID has no matching customer record "
     f"(referential-integrity check, needed before loading into SQL with a foreign key)")

note(f"  purchases final shape: {purchases.shape}")

# ---------------------------------------------------------------------------
# 5. REVIEWS: standardize rating scale, missing values, referential integrity
# ---------------------------------------------------------------------------
note("\nCLEANING reviews")
before = len(reviews)
reviews = reviews.dropna(subset=["Review_ID"])
note(f"  dropped {before - len(reviews)} rows with missing Review_ID")

before = len(reviews)
reviews = reviews.dropna(subset=["Customer_ID", "Product_ID"])
note(f"  dropped {before - len(reviews)} rows with missing Customer_ID or Product_ID")

# The Rating column mixes two scales: numeric 1-5 and the text labels
# 'poor' / 'excellent'. Standardize everything onto the numeric 1-5 scale
# (poor -> 1, excellent -> 5, matching the low/high ends of the numeric scale).
rating_map = {"poor": 1, "excellent": 5}
raw_rating = reviews["Rating"].astype(str).str.strip().str.lower()
n_text_ratings = raw_rating.isin(rating_map.keys()).sum()
reviews["Rating"] = raw_rating.map(lambda v: rating_map.get(v, v))
reviews["Rating"] = pd.to_numeric(reviews["Rating"], errors="coerce")
note(f"  standardized {n_text_ratings} text ratings ('poor'/'excellent') onto the numeric 1-5 scale")

rating_median = reviews["Rating"].median()
n_missing_rating = reviews["Rating"].isnull().sum()
reviews["Rating"] = reviews["Rating"].fillna(rating_median).astype("int64")
note(f"  imputed {n_missing_rating} missing Rating values with the median rating ({rating_median:.0f})")

n_missing_text = reviews["Review_Text"].isnull().sum()
reviews["Review_Text"] = reviews["Review_Text"].fillna("No review text provided")
note(f"  filled {n_missing_text} missing Review_Text values with a placeholder")

reviews["Review_ID"] = reviews["Review_ID"].astype("int64")
reviews["Product_ID"] = reviews["Product_ID"].astype("int64")
reviews["Customer_ID"] = reviews["Customer_ID"].astype("int64")

reviews = reviews.drop_duplicates(subset=["Review_ID"], keep="first")

before = len(reviews)
reviews = reviews[reviews["Customer_ID"].isin(customers["Customer_ID"])]
note(f"  dropped {before - len(reviews)} rows whose Customer_ID has no matching customer record")

# Sentiment: the review text in this dataset is auto-generated filler
# text (not genuine customer language), so a real NLP sentiment model
# would score it close to random. The Rating is the reliable sentiment
# signal here, so it drives Sentiment_Category. A lightweight lexicon
# score on the text is included too, for completeness / demonstration.
reviews["Sentiment_Category"] = pd.cut(
    reviews["Rating"], bins=[0, 2, 3, 5], labels=["Negative", "Neutral", "Positive"]
)
reviews["Text_Sentiment_Score"] = reviews["Review_Text"].apply(text_sentiment_score)

note(f"  reviews final shape: {reviews.shape}")

# ---------------------------------------------------------------------------
# 6. PRODUCTS dimension (derived - no product master file was supplied)
# ---------------------------------------------------------------------------
product_ids = pd.Index(purchases["Product_ID"]).union(reviews["Product_ID"]).unique()
products = pd.DataFrame({"Product_ID": sorted(product_ids)})
note(f"\nDerived products dimension: {len(products)} distinct products referenced "
     f"in purchases and/or reviews")

# ---------------------------------------------------------------------------
# 7. EXPORT
# ---------------------------------------------------------------------------
customers.to_csv(f"{OUT_DIR}/cleaned_customer_data.csv", index=False)
purchases.to_csv(f"{OUT_DIR}/cleaned_purchase_history.csv", index=False)
reviews.to_csv(f"{OUT_DIR}/cleaned_product_reviews.csv", index=False)
products.to_csv(f"{OUT_DIR}/cleaned_products.csv", index=False)

with open(f"{OUT_DIR}/data_cleaning_log.txt", "w") as f:
    f.write("\n".join(log))

note(f"\nSaved cleaned files to {OUT_DIR}")
note(f"FINAL ROW COUNTS -> customers: {len(customers)}, purchases: {len(purchases)}, "
     f"reviews: {len(reviews)}, products: {len(products)}")
