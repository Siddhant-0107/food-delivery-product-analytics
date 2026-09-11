import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
N_ORDERS = 250_000
OUT = Path("data")
rng = np.random.default_rng(SEED)

def main():
    OUT.mkdir(exist_ok=True)
    n_users, n_restaurants, n_riders = 30000, 900, 700

    users = pd.DataFrame({
        "user_id": np.arange(1, n_users + 1),
        "signup_date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 365, n_users), unit="D"),
        "acquisition_channel": rng.choice(["Organic","Ads","Referral","Social"], n_users, p=[.42,.24,.19,.15])
    })

    restaurants = pd.DataFrame({
        "restaurant_id": np.arange(1, n_restaurants + 1),
        "cuisine": rng.choice(["North Indian","South Indian","Chinese","Fast Food","Biryani","Pizza","Healthy"], n_restaurants),
        "rating": np.clip(rng.normal(4.1, .35, n_restaurants), 2.5, 5.0).round(2),
        "prep_capacity": rng.integers(15, 90, n_restaurants)
    })

    riders = pd.DataFrame({
        "rider_id": np.arange(1, n_riders + 1),
        "experience_months": rng.integers(1, 60, n_riders)
    })

    start = pd.Timestamp("2025-01-01")
    ts = start + pd.to_timedelta(rng.integers(0, 180*24*60, N_ORDERS), unit="m")
    hour = ts.hour
    weekend = (ts.dayofweek >= 5).astype(int)

    restaurant_id = rng.integers(1, n_restaurants + 1, N_ORDERS)
    user_id = rng.integers(1, n_users + 1, N_ORDERS)
    rider_id = rng.integers(1, n_riders + 1, N_ORDERS)

    traffic = rng.choice(["Low","Medium","High"], N_ORDERS, p=[.38,.44,.18])
    weather = rng.choice(["Clear","Cloudy","Rain"], N_ORDERS, p=[.62,.25,.13])
    distance = np.clip(rng.gamma(2.2, 1.7, N_ORDERS), .4, 14)
    basket = np.clip(rng.lognormal(5.0, .55, N_ORDERS), 120, 2500)
    items = rng.integers(1, 7, N_ORDERS)

    peak = ((hour >= 12) & (hour <= 14) | (hour >= 19) & (hour <= 22)).astype(int)
    traffic_penalty = np.select([traffic=="Low", traffic=="Medium", traffic=="High"], [0, 7, 16])
    weather_penalty = np.select([weather=="Clear", weather=="Cloudy", weather=="Rain"], [0, 3, 9])
    prep = np.clip(rng.normal(18 + 5*peak, 5, N_ORDERS), 7, 45)
    travel = 8 + 3.1*distance + traffic_penalty*.45 + weather_penalty*.35 + rng.normal(0, 4, N_ORDERS)
    eta = np.clip(prep + travel, 10, 95)
    delivered = rng.random(N_ORDERS) > (.035 + .035*(traffic=="High") + .025*(weather=="Rain"))
    cancel_prob = 1/(1+np.exp(-(eta-48)/8))
    cancelled = (~delivered) | (rng.random(N_ORDERS) < .035*cancel_prob)
    delivered = ~cancelled

    base_price = basket
    surge = 1 + .04*peak + .07*(traffic=="High") + .05*(weather=="Rain")
    price = base_price * surge
    discount = np.where(rng.random(N_ORDERS) < .22, rng.uniform(.05,.25,N_ORDERS), 0)
    revenue = np.where(delivered, price*(1-discount), 0)

    orders = pd.DataFrame({
        "order_id": np.arange(1, N_ORDERS+1),
        "user_id": user_id,
        "restaurant_id": restaurant_id,
        "rider_id": rider_id,
        "order_ts": ts,
        "hour": hour,
        "weekend": weekend,
        "traffic": traffic,
        "weather": weather,
        "distance_km": distance.round(2),
        "items": items,
        "basket_value": basket.round(2),
        "listed_price": price.round(2),
        "discount_pct": discount.round(3),
        "eta_minutes": eta.round(2),
        "cancelled": cancelled.astype(int),
        "delivered": delivered.astype(int),
        "revenue": revenue.round(2)
    })

    for df, name in [(users,"users"),(restaurants,"restaurants"),(riders,"riders"),(orders,"orders")]:
        df.to_csv(OUT / f"{name}.csv", index=False)

    print(f"Generated {len(orders):,} orders.")

if __name__ == "__main__":
    main()
