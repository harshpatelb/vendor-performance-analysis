"""
STEP 1 OF THE PIPELINE — Load raw CSV files into a SQLite database.

What this does:
    Reads every .csv file inside the /data folder and writes each one into
    its own table inside inventory.db (table name = file name).

Why a database instead of just reading CSVs in pandas:
    The raw files here (purchases, sales, purchase_prices, vendor_invoice)
    are large. SQL lets us filter, join and aggregate them efficiently
    with a single query instead of loading everything into memory.

How to run:
    python scripts/ingestion_db.py
    (expects raw CSVs inside a local ./data folder)
"""

import logging
import os
import time

import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
)

engine = create_engine("sqlite:///inventory.db")


def ingest_db(df: pd.DataFrame, table_name: str, engine) -> None:
    """Write a dataframe to a database table, replacing it if it exists."""
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)


def load_raw_data(data_folder: str = "data") -> None:
    """Load every CSV in `data_folder` into its own table in inventory.db."""
    start = time.time()

    for file_name in os.listdir(data_folder):
        if file_name.endswith(".csv"):
            table_name = file_name[:-4]
            df = pd.read_csv(os.path.join(data_folder, file_name))
            logging.info(f"Ingesting {file_name} -> table '{table_name}'")
            ingest_db(df, table_name, engine)

    minutes_taken = (time.time() - start) / 60
    logging.info(f"Ingestion complete. Total time: {minutes_taken:.2f} minutes")


if __name__ == "__main__":
    load_raw_data()
