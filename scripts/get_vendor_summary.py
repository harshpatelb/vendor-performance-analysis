"""
STEP 2 OF THE PIPELINE — Build one clean "vendor_sales_summary" table.

Why this table exists:
    The raw database has 4 separate tables (purchases, purchase_prices,
    sales, vendor_invoice). Every useful business question needs data
    from more than one of them, joined and aggregated by vendor + brand.
    Instead of re-running that expensive join every time, we build it
    once here and save the result as its own table (and CSV).

Steps performed:
    1. Combine purchase, sales and freight data per vendor/brand (SQL).
    2. Clean the result (fix data types, fill missing values, trim text).
    3. Add a few business metrics (gross profit, profit margin, etc).
    4. Save the result back into the database.

How to run:
    python scripts/get_vendor_summary.py
    (expects inventory.db already populated by ingestion_db.py)
"""

import logging
import sqlite3

import pandas as pd

logging.basicConfig(
    filename="logs/get_vendor_summary.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
)

SUMMARY_QUERY = """
WITH FreightSummary AS (
    SELECT
        VendorNumber,
        SUM(Freight) AS FreightCost
    FROM vendor_invoice
    GROUP BY VendorNumber
),

PurchaseSummary AS (
    SELECT
        p.VendorNumber,
        p.VendorName,
        p.Brand,
        p.Description,
        p.PurchasePrice,
        pp.Price AS ActualPrice,
        pp.Volume,
        SUM(p.Quantity) AS TotalPurchaseQuantity,
        SUM(p.Dollars) AS TotalPurchaseDollars
    FROM purchases p
    JOIN purchase_prices pp
        ON p.Brand = pp.Brand
    WHERE p.PurchasePrice > 0
    GROUP BY p.VendorNumber, p.VendorName, p.Brand, p.Description,
             p.PurchasePrice, pp.Price, pp.Volume
),

SalesSummary AS (
    SELECT
        VendorNo,
        Brand,
        SUM(SalesQuantity) AS TotalSalesQuantity,
        SUM(SalesDollars) AS TotalSalesDollars,
        SUM(SalesPrice) AS TotalSalesPrice,
        SUM(ExciseTax) AS TotalExciseTax
    FROM sales
    GROUP BY VendorNo, Brand
)

SELECT
    ps.VendorNumber,
    ps.VendorName,
    ps.Brand,
    ps.Description,
    ps.PurchasePrice,
    ps.ActualPrice,
    ps.Volume,
    ps.TotalPurchaseQuantity,
    ps.TotalPurchaseDollars,
    ss.TotalSalesQuantity,
    ss.TotalSalesDollars,
    ss.TotalSalesPrice,
    ss.TotalExciseTax,
    fs.FreightCost
FROM PurchaseSummary ps
LEFT JOIN SalesSummary ss
    ON ps.VendorNumber = ss.VendorNo AND ps.Brand = ss.Brand
LEFT JOIN FreightSummary fs
    ON ps.VendorNumber = fs.VendorNumber
ORDER BY ps.TotalPurchaseDollars DESC
"""


def ingest_db(df: pd.DataFrame, table_name: str, engine) -> None:
    """Write a dataframe to a database table, replacing it if it exists."""
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)


def create_vendor_summary(conn) -> pd.DataFrame:
    """Join purchases, sales and freight data into one vendor/brand table."""
    return pd.read_sql_query(SUMMARY_QUERY, conn)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Fix types, fill gaps, trim text, and add derived business metrics."""
    df["Volume"] = df["Volume"].astype("float")
    df.fillna(0, inplace=True)

    df["VendorName"] = df["VendorName"].str.strip()
    df["Description"] = df["Description"].str.strip()

    # Derived metrics used throughout the analysis
    df["GrossProfit"] = df["TotalSalesDollars"] - df["TotalPurchaseDollars"]
    df["ProfitMargin"] = (df["GrossProfit"] / df["TotalSalesDollars"]) * 100
    df["StockTurnover"] = df["TotalSalesQuantity"] / df["TotalPurchaseQuantity"]
    df["SalesToPurchaseRatio"] = df["TotalSalesDollars"] / df["TotalPurchaseDollars"]

    return df


if __name__ == "__main__":
    conn = sqlite3.connect("inventory.db")

    logging.info("Building vendor summary table...")
    summary_df = create_vendor_summary(conn)

    logging.info("Cleaning data...")
    clean_df = clean_data(summary_df)

    logging.info("Saving to database as 'vendor_sales_summary'...")
    ingest_db(clean_df, "vendor_sales_summary", conn)

    clean_df.to_csv("data/vendor_sales_summary.csv", index=False)
    logging.info("Done. Also exported to data/vendor_sales_summary.csv")
