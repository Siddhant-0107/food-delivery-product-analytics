from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

FEATURES = [
    "hour",
    "dow",
    "day",
    "month",
    "is_weekend",
    "lag_1",
    "lag_24",
    "lag_168",
    "rolling_24",
    "rolling_168",
]


def build_hourly_series(orders: pd.DataFrame) -> pd.DataFrame:
    df = orders.copy()
    df["order_ts"] = pd.to_datetime(df["order_ts"])

    hourly = (
        df.set_index("order_ts")
        .resample("h")
        .agg(orders=("order_id", "count"), revenue=("revenue", "sum"))
        .reset_index()
        .sort_values("order_ts")
    )

    hourly["hour"] = hourly["order_ts"].dt.hour
    hourly["dow"] = hourly["order_ts"].dt.dayofweek
    hourly["day"] = hourly["order_ts"].dt.day
    hourly["month"] = hourly["order_ts"].dt.month
    hourly["is_weekend"] = (hourly["dow"] >= 5).astype(int)
    hourly["lag_1"] = hourly["orders"].shift(1)
    hourly["lag_24"] = hourly["orders"].shift(24)
    hourly["lag_168"] = hourly["orders"].shift(168)
    hourly["rolling_24"] = hourly["orders"].shift(1).rolling(24).mean()
    hourly["rolling_168"] = hourly["orders"].shift(1).rolling(168).mean()

    return hourly.dropna().reset_index(drop=True)


def train_demand_model(orders: pd.DataFrame):
    """Train an ML benchmark and persist it for comparison."""
    df = build_hourly_series(orders)
    split = int(len(df) * 0.83)
    train, test = df.iloc[:split], df.iloc[split:]

    model = HistGradientBoostingRegressor(
        max_iter=250,
        learning_rate=0.06,
        max_leaf_nodes=31,
        l2_regularization=1.0,
        random_state=42,
    )
    model.fit(train[FEATURES], train["orders"])

    pred = np.maximum(model.predict(test[FEATURES]), 0)
    mae = mean_absolute_error(test["orders"], pred)
    rmse = mean_squared_error(test["orders"], pred) ** 0.5

    joblib.dump(
        {"model": model, "features": FEATURES},
        MODEL_DIR / "demand_model.joblib",
    )

    return {
        "demand_mae": float(mae),
        "demand_rmse": float(rmse),
        "test_hours": int(len(test)),
    }


def forecast_next_24(orders: pd.DataFrame) -> pd.DataFrame:
    """Forecast the next 24 hours using a seasonal-naive weekly baseline.

    The project data has a strong repeated hour-of-day/weekday pattern, so the
    same hour from recent weeks is a more transparent operational forecast than
    recursively feeding unstable ML predictions back into the model.
    """
    hourly = build_hourly_series(orders)
    raw = (
        orders.assign(order_ts=pd.to_datetime(orders["order_ts"]))
        .set_index("order_ts")
        .resample("h")
        .agg(orders=("order_id", "count"))
        .reset_index()
        .sort_values("order_ts")
    )

    if len(raw) < 24 * 8:
        raise ValueError("At least 8 weeks of hourly history are required for the weekly seasonal forecast.")

    raw["dow"] = raw["order_ts"].dt.dayofweek
    raw["hour"] = raw["order_ts"].dt.hour

    # Forecast each future hour from the mean of the same hour across the
    # previous four matching weekdays, with a small recent-level adjustment.
    recent_level = float(raw["orders"].tail(24 * 7).mean())
    overall_level = float(raw["orders"].tail(24 * 28).mean())
    level_ratio = recent_level / overall_level if overall_level else 1.0
    level_ratio = float(np.clip(level_ratio, 0.90, 1.10))

    last_ts = raw["order_ts"].iloc[-1]
    rows = []
    history = raw.set_index("order_ts")["orders"]

    for step in range(1, 25):
        ts = last_ts + pd.Timedelta(hours=step)
        target_dow = ts.dayofweek
        target_hour = ts.hour

        same_slots = raw[
            (raw["dow"] == target_dow) & (raw["hour"] == target_hour)
        ].tail(4)
        seasonal = float(same_slots["orders"].mean()) if not same_slots.empty else recent_level

        # Mildly adapt the seasonal pattern to the latest weekly level.
        forecast = max(seasonal * level_ratio, 0.0)
        rows.append({"order_ts": ts, "forecast_orders": forecast})

    return pd.DataFrame(rows)
