from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.model_selection import train_test_split

# Streamlit Cloud does not retain locally generated data/model artifacts.
# Generate the synthetic dataset on first startup so the dashboard can run
# without committing large generated CSV files to GitHub.
DATA_DIR = Path("data")
MODEL_DIR = Path("models")
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)


def _ensure_data():
    if not (DATA_DIR / "orders.csv").exists():
        from generate_data import main as generate_data
        generate_data()


def _features(df):
    x = df[['distance_km','items','basket_value','hour','weekend','traffic','weather']].copy()
    x['traffic'] = x['traffic'].map({'Low':0,'Medium':1,'High':2}).astype(int)
    x['weather'] = x['weather'].map({'Clear':0,'Cloudy':1,'Rain':2}).astype(int)
    return x


def train_models(orders):
    x = _features(orders)
    Xtr, Xte, ytr, yte = train_test_split(x, orders['eta_minutes'], test_size=.2, random_state=42)
    eta_model = HistGradientBoostingRegressor(max_iter=180, learning_rate=.08, max_leaf_nodes=31, random_state=42)
    eta_model.fit(Xtr, ytr)
    eta_mae = mean_absolute_error(yte, eta_model.predict(Xte))
    joblib.dump(eta_model, MODEL_DIR / 'eta_model.joblib')

    Xtr, Xte, ytr, yte = train_test_split(x, orders['cancelled'], test_size=.2, random_state=42, stratify=orders['cancelled'])
    cancel_model = HistGradientBoostingClassifier(max_iter=160, learning_rate=.08, max_leaf_nodes=31, random_state=42)
    cancel_model.fit(Xtr, ytr)
    auc = roc_auc_score(yte, cancel_model.predict_proba(Xte)[:,1])
    joblib.dump(cancel_model, MODEL_DIR / 'cancel_model.joblib')
    return {'eta_mae': float(eta_mae), 'cancel_auc': float(auc)}


def load_model(name):
    _ensure_data()
    model_path = MODEL_DIR / name
    if not model_path.exists():
        orders = pd.read_csv(DATA_DIR / 'orders.csv')
        train_models(orders)
    return joblib.load(model_path)


# Prepare artifacts automatically when the module is imported by the dashboard.
_ensure_data()
if not (MODEL_DIR / 'eta_model.joblib').exists() or not (MODEL_DIR / 'cancel_model.joblib').exists():
    train_models(pd.read_csv(DATA_DIR / 'orders.csv'))
