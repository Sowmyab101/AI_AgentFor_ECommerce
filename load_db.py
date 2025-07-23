import pandas as pd
import sqlite3

# Load your actual datasets
ad_sales = pd.read_csv("data/ad_sales.csv")
total_sales = pd.read_csv("data/total_sales.csv")
eligibility = pd.read_csv("data/eligibility.csv")

# Create DB and save
conn = sqlite3.connect("ecommerce1.db")
ad_sales.to_sql("ad_sales", conn, if_exists="replace", index=False)
total_sales.to_sql("total_sales", conn, if_exists="replace", index=False)
eligibility.to_sql("eligibility", conn, if_exists="replace", index=False)
conn.close()

print("✅ All tables loaded into ecommerce1.db")
