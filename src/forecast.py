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
    "hour_mean_7d",
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

    # Recent same-hour demand baseline, using only prior days.
    hourly["date"] = hourly["order_ts"].dt.date
    by_hour_day = hourly.groupby(["date", "hour"], as_index=False)["orders"].mean()
    by_hour_day["hour_mean_7d"] = by_hour_day.groupby("hour")["orders"].transform(
        lambda s: s.shift(1).rolling(7, min_periods=2).mean()
    )
    hourly = hourly.merge(
        by_hour_day[["date", "hour", "hour_mean_7d"]],
        on=["date", "hour"],
        how="left",
        suffixes=("", "_hist"),
    )
    hourly["hour_mean_7d"] = hourly["hour_mean_7d_hist"]
    hourly.drop(columns=["hour_mean_7d_hist", "date"], inplace=True)

    return hourly.dropna().reset_index(drop=True)


def train_demand_model(orders: pd.DataFrame):
    df = build_hourly_series(orders)
    split = int(len(df) * 0.83)
    train, test = df.iloc[:split], df.iloc[split:]

    model = HistGradientBoostingRegressor(
        max_iter=300,
        learning_rate=0.05,
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
    """Forecast the next 24 hourly order counts from the latest observed hour."""
    artifact = joblib.load(MODEL_DIR / "demand_model.joblib")
    model = artifact["model"]
    features = artifact.get("features", FEATURES)

    hourly = build_hourly_series(orders)
    history = hourly[["order_ts", "orders"]].copy()

    # Same-hour baselines from the last seven observed occurrences of each hour.
    history["hour"] = history["order_ts"].dt.hour
    recent_by_hour = {}
    for hour in range(24):
        recent = history.loc[history["hour"] == hour, "orders"].tail(7)
        recent_by_hour[hour] = float(recent.mean()) if not recent.empty else float(history["orders"].mean())

    rows = []
    for _ in range(24):
        ts = history["order_ts"].iloc[-1] + pd.Timedelta(hours=1)
        vals = history["orders"].to_numpy(dtype=float)
        current_hour = int(ts.hour)

        row = {
            "hour": current_hour,
            "dow": ts.dayofweek,
            "day": ts.day,
            "month": ts.month,
            "is_weekend": int(ts.dayofweek >= 5),
            "lag_1": vals[-1],
            "lag_24": vals[-24],
            "lag_168": vals[-168],
            "rolling_24": float(vals[-24:].mean()),
            "rolling_168": float(vals[-168:].mean()),
            "hour_mean_7d": recent_by_hour.get(current_hour, float(vals.mean())),
        }

        model_pred = float(model.predict(pd.DataFrame([row])[features])[0])
        baseline = recent_by_hour.get(current_hour, float(vals.mean()))

        # Blend the learned model with the empirical same-hour baseline so that
        # the forecast preserves the observed daily demand profile.
        pred = 0.5 * model_pred + 0.5 * baseline
        pred = max(pred, 0.0)

        rows.append({"order_ts": ts, "forecast_orders": pred})
        history = pd.concat(
            [history, pd.DataFrame([{ "order_ts": ts, "orders": pred, "hour": current_hour }])],
            ignore_index=True,
        )

    return pd.DataFrame(rows)
