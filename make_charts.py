import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

RES = os.path.join(os.path.dirname(__file__), "..", "sql", "query_results")
OUT = os.path.join(os.path.dirname(__file__), "..", "powerbi", "charts")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})
NAVY = "#1f3b57"
TEAL = "#2a9d8f"
CORAL = "#e76f51"
GOLD = "#e9c46a"
GREY = "#8d99ae"

# 1. Top products by units sold
df = pd.read_csv(f"{RES}/01_most_purchased_products.csv")
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(df["product_id"].astype(str), df["total_units_sold"], color=NAVY)
ax.set_xlabel("Total units sold")
ax.set_ylabel("Product ID")
ax.set_title("Top 10 Most Purchased Products")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUT}/01_top_products.png", dpi=150)
plt.close()

# 2. Top customers by LTV
df = pd.read_csv(f"{RES}/02_top_customers_by_lifetime_value.csv")
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(df["name"], df["lifetime_value"], color=TEAL)
ax.set_xlabel("Lifetime value ($)")
ax.set_title("Top 10 Customers by Lifetime Value")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUT}/02_top_customers.png", dpi=150)
plt.close()

# 3. Product rating summary (top reviewed)
df = pd.read_csv(f"{RES}/03_product_rating_summary.csv")
fig, ax = plt.subplots(figsize=(8, 5))
colors = [CORAL if v < 3 else GOLD if v < 4 else TEAL for v in df["avg_rating"]]
ax.barh(df["product_id"].astype(str), df["avg_rating"], color=colors)
ax.set_xlabel("Average rating (1-5)")
ax.set_ylabel("Product ID")
ax.set_title("Average Rating - Most-Reviewed Products")
ax.set_xlim(0, 5)
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUT}/03_product_ratings.png", dpi=150)
plt.close()

# 4. Regional sales distribution
df = pd.read_csv(f"{RES}/04_regional_sales_distribution.csv")
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(df["location"], df["total_revenue"], color=NAVY)
ax.set_xlabel("Total revenue ($)")
ax.set_title("Top 15 Locations by Sales Revenue")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUT}/04_regional_sales.png", dpi=150)
plt.close()

# 5. Monthly sales trend
df = pd.read_csv(f"{RES}/05_product_popularity_trend_by_month.csv")
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(df["month"], df["revenue"], marker="o", color=NAVY, linewidth=2)
ax.set_ylabel("Revenue ($)")
ax.set_title("Monthly Sales Revenue Trend")
ax.tick_params(axis="x", rotation=60)
plt.tight_layout()
plt.savefig(f"{OUT}/05_monthly_trend.png", dpi=150)
plt.close()

# 6. Sentiment distribution donut
df = pd.read_csv(f"{RES}/06_sentiment_distribution.csv")
colors_map = {"Positive": TEAL, "Neutral": GOLD, "Negative": CORAL}
colors = [colors_map[c] for c in df["sentiment_category"]]
fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    df["number_of_reviews"], labels=df["sentiment_category"], colors=colors,
    autopct="%1.0f%%", startangle=90, wedgeprops=dict(width=0.4)
)
ax.set_title("Customer Sentiment Distribution\n(derived from star rating)")
plt.tight_layout()
plt.savefig(f"{OUT}/06_sentiment.png", dpi=150)
plt.close()

# 8. Age band spending
df = pd.read_csv(f"{RES}/08_age_band_spending_profile.csv")
order = ["Under 25", "25-34", "35-44", "45-54", "55-64", "65+"]
df["age_band"] = pd.Categorical(df["age_band"], categories=order, ordered=True)
df = df.sort_values("age_band")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(df["age_band"].astype(str), df["total_revenue"], color=TEAL)
ax.set_ylabel("Total revenue ($)")
ax.set_title("Revenue by Customer Age Band")
plt.tight_layout()
plt.savefig(f"{OUT}/08_age_band.png", dpi=150)
plt.close()

print("Charts written to", OUT)
print(os.listdir(OUT))
