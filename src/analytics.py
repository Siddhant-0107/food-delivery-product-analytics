from pathlib import Path
import duckdb
import pandas as pd

DB = Path("data/food_delivery.duckdb")

def build_db():
    DB.parent.mkdir(exist_ok=True)
    con = duckdb.connect(str(DB))
    for table in ["users","restaurants","riders","orders"]:
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv_auto('data/{table}.csv')")
    return con

def query(sql: str):
    con = duckdb.connect(str(DB))
    try:
        return con.execute(sql).df()
    finally:
        con.close()
