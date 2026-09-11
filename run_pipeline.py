import json
from pathlib import Path
import pandas as pd
from generate_data import main as generate
from src.analytics import build_db
from src.models import train_models
from src.forecast import train_demand_model


def main():
    generate()
    con = build_db()
    con.close()
    orders = pd.read_csv('data/orders.csv')
    metrics = {}
    metrics.update(train_models(orders))
    metrics.update(train_demand_model(orders))
    Path('artifacts').mkdir(exist_ok=True)
    Path('artifacts/metrics.json').write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
    print('Pipeline complete. Dashboard: streamlit run app.py')
    print('API: uvicorn api:app --reload')

if __name__ == '__main__':
    main()
