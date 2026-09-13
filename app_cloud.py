from pathlib import Path

import pandas as pd

from generate_data import main as generate_data
from src.models import train_models


DATA_FILE = Path("data/orders.csv")
ETA_MODEL = Path("models/eta_model.joblib")
CANCEL_MODEL = Path("models/cancel_model.joblib")


# Streamlit Cloud does not keep locally generated data/model artifacts from the repository.
# Bootstrap them once when the app starts.
if not DATA_FILE.exists():
    generate_data()

if not ETA_MODEL.exists() or not CANCEL_MODEL.exists():
    orders = pd.read_csv(DATA_FILE)
    train_models(orders)

# Run the existing dashboard after the required local artifacts exist.
import app  # noqa: E402,F401
