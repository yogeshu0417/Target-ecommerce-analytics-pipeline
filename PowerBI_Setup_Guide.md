# Phase 3 — Power BI Setup Guide

Power BI Desktop is a Windows application, so it can't be run inside this
environment — this guide gives you the exact steps, data model, and DAX to
build the three required dashboards yourself. The `charts/` folder in this
package shows what the finished visuals should look like, built from the
same cleaned data.

## 1. Connect Power BI to the data

**Option A — straight from the cleaned CSVs (fastest):**
1. Power BI Desktop → **Get Data** → **Text/CSV**.
2. Load `cleaned_customer_data.csv`, `cleaned_purchase_history.csv`,
   `cleaned_product_reviews.csv`, `cleaned_products.csv`.
3. In **Power Query Editor**, confirm `Registration_Date`/`Purchase_Date`
   are typed as `Date` and ID columns as `Whole Number`, then **Close & Apply**.

**Option B — from the SQL database (matches the Phase 2 brief):**
1. Load `ecommerce.db`/the PostgreSQL database created from `schema_postgresql.sql`.
2. Power BI Desktop → **Get Data** → **PostgreSQL database** (or **ODBC** for
   SQL Server) → enter the server/database → **Import** mode.
3. Select the `customers`, `products`, `purchases`, `reviews` tables.

## 2. Build the data model

In **Model view**, create these relationships (drag field to field):

| From | To | Cardinality |
|---|---|---|
| `purchases[customer_id]` | `customers[customer_id]` | Many-to-one |
| `purchases[product_id]` | `products[product_id]` | Many-to-one |
| `reviews[customer_id]` | `customers[customer_id]` | Many-to-one |
| `reviews[product_id]` | `products[product_id]` | Many-to-one |

This gives a standard star schema: `customers` and `products` as
dimensions, `purchases` and `reviews` as fact tables.

## 3. Key DAX measures

Create a new **Measure** (Modeling tab → New Measure) for each of these,
attached to the relevant table:

```DAX
Total Revenue = SUM(purchases[total_price])

Total Units Sold = SUM(purchases[quantity])

Number of Orders = COUNTROWS(purchases)

Average Order Value = DIVIDE([Total Revenue], [Number of Orders])

Customer Lifetime Value =
    CALCULATE([Total Revenue], ALLEXCEPT(purchases, purchases[customer_id]))

Average Rating = AVERAGE(reviews[rating])

Number of Reviews = COUNTROWS(reviews)

Positive Review % =
    DIVIDE(
        CALCULATE(COUNTROWS(reviews), reviews[sentiment_category] = "Positive"),
        [Number of Reviews]
    )

Negative Review % =
    DIVIDE(
        CALCULATE(COUNTROWS(reviews), reviews[sentiment_category] = "Negative"),
        [Number of Reviews]
    )
```

## 4. Build the three dashboard pages

### Page 1 — Regional Sales Distribution
- **Filled map or bar chart**: `customers[location]` on axis, `[Total Revenue]` on values.
  Note: `Location` in this dataset is a fictional, near-unique city per
  customer (2,583 distinct values across 2,909 customers) — there is no
  state/country field to roll up to. A bar chart of the top 15–20 locations
  (as in `charts/04_regional_sales.png`) reads better than a map here; if a
  real state/region column becomes available, swap it in for a cleaner map.
- **Card**: `[Total Revenue]`, `[Number of Orders]`.
- **Slicer**: `purchases[purchase_date]` (date range).

### Page 2 — Product Popularity Trends
- **Line chart**: `purchases[purchase_date]` (Month) on axis, `[Total Units Sold]`
  and `[Total Revenue]` on values — see `charts/05_monthly_trend.png`.
- **Bar chart**: `products[product_id]` on axis, `[Total Units Sold]` on
  values, top N filter = 10 — see `charts/01_top_products.png`.
- **Table**: top 10 products with units sold, revenue, and average rating
  (via a relationship-based lookup measure or a merged query in Power Query).

### Page 3 — Customer Sentiment Analysis
- **Donut chart**: `reviews[sentiment_category]` on legend, `[Number of Reviews]`
  on values — see `charts/06_sentiment.png`.
- **Bar chart**: `products[product_id]` on axis, `[Positive Review %]` and
  `[Negative Review %]` on values, for the most-reviewed products.
- **Card**: `[Average Rating]` overall.
- **Note on sentiment method**: `Review_Text` in the source data is
  auto-generated filler text, not genuine customer language, so an NLP
  sentiment model on the text would score close to random. `Sentiment_Category`
  is instead derived directly from the star `Rating` (1–2 = Negative,
  3 = Neutral, 4–5 = Positive), which is the reliable signal available.
  A lightweight lexicon score on the text (`Text_Sentiment_Score`) is
  included too, for completeness — swap in a real NLP model
  (Cognitive Services Text Analytics, or a Python/R visual with
  TextBlob/VADER) if real review text is ever collected.

## 5. Bonus cut worth adding
`charts/08_age_band.png` — revenue by customer age band — is a useful extra
slicer/visual for the customer page (`Age` bucketed into `Under 25 / 25-34 /
35-44 / 45-54 / 55-64 / 65+`); add it as a calculated column on `customers`
if you want it as a slicer.
