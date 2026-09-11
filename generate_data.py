import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
N_ORDERS = 250_000
N_BROWSE_SESSIONS = 150_000
N_EXPERIMENT_SESSIONS = 60_000
OUT = Path("data")
rng = np.random.default_rng(SEED)


def sample_order_timestamps(n, start, days):
    """Sample timestamps with lunch/dinner peaks and weekend uplift."""
    day_idx = rng.integers(0, days, n)
    is_weekend = ((start + pd.to_timedelta(day_idx, unit="D")).dayofweek >= 5)

    hours = np.arange(24)
    base = np.full(24, 0.55)
    base[7:11] = 0.75
    base[11:15] = 1.65
    base[15:18] = 0.85
    base[18:23] = 2.10
    base[23] = 0.65

    hour_probs_weekday = base / base.sum()
    hour_probs_weekend = base.copy()
    hour_probs_weekend[11:15] *= 1.12
    hour_probs_weekend[18:23] *= 1.18
    hour_probs_weekend = hour_probs_weekend / hour_probs_weekend.sum()

    sampled_hour = np.empty(n, dtype=int)
    wk = np.flatnonzero(is_weekend)
    wd = np.flatnonzero(~is_weekend)
    sampled_hour[wd] = rng.choice(hours, len(wd), p=hour_probs_weekday)
    sampled_hour[wk] = rng.choice(hours, len(wk), p=hour_probs_weekend)
    minute = rng.integers(0, 60, n)

    return start + pd.to_timedelta(day_idx, unit="D") + pd.to_timedelta(sampled_hour, unit="h") + pd.to_timedelta(minute, unit="m")


def main():
    OUT.mkdir(exist_ok=True)
    n_users, n_restaurants, n_riders = 30000, 900, 700

    users = pd.DataFrame({
        "user_id": np.arange(1, n_users + 1),
        "signup_date": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 365, n_users), unit="D"),
        "acquisition_channel": rng.choice(["Organic", "Ads", "Referral", "Social"], n_users, p=[.42, .24, .19, .15])
    })

    restaurants = pd.DataFrame({
        "restaurant_id": np.arange(1, n_restaurants + 1),
        "cuisine": rng.choice(["North Indian", "South Indian", "Chinese", "Fast Food", "Biryani", "Pizza", "Healthy"], n_restaurants),
        "rating": np.clip(rng.normal(4.1, .35, n_restaurants), 2.5, 5.0).round(2),
        "prep_capacity": rng.integers(15, 90, n_restaurants)
    })

    riders = pd.DataFrame({
        "rider_id": np.arange(1, n_riders + 1),
        "experience_months": rng.integers(1, 60, n_riders)
    })

    start = pd.Timestamp("2025-01-01")
    ts = sample_order_timestamps(N_ORDERS, start, 180)
    hour = ts.hour
    weekend = (ts.dayofweek >= 5).astype(int)

    restaurant_id = rng.integers(1, n_restaurants + 1, N_ORDERS)
    user_id = rng.integers(1, n_users + 1, N_ORDERS)
    rider_id = rng.integers(1, n_riders + 1, N_ORDERS)

    traffic = rng.choice(["Low", "Medium", "High"], N_ORDERS, p=[.38, .44, .18])
    weather = rng.choice(["Clear", "Cloudy", "Rain"], N_ORDERS, p=[.62, .25, .13])
    distance = np.clip(rng.gamma(2.2, 1.7, N_ORDERS), .4, 14)
    basket = np.clip(rng.lognormal(5.0, .55, N_ORDERS), 120, 2500)
    items = rng.integers(1, 7, N_ORDERS)

    peak = ((hour >= 12) & (hour <= 14) | (hour >= 19) & (hour <= 22)).astype(int)
    traffic_penalty = np.select([traffic == "Low", traffic == "Medium", traffic == "High"], [0, 7, 16])
    weather_penalty = np.select([weather == "Clear", weather == "Cloudy", weather == "Rain"], [0, 3, 9])
    prep = np.clip(rng.normal(18 + 5 * peak, 5, N_ORDERS), 7, 45)
    travel = 8 + 3.1 * distance + traffic_penalty * .45 + weather_penalty * .35 + rng.normal(0, 4, N_ORDERS)
    eta = np.clip(prep + travel, 10, 95)
    delivered = rng.random(N_ORDERS) > (.035 + .035 * (traffic == "High") + .025 * (weather == "Rain"))
    cancel_prob = 1 / (1 + np.exp(-(eta - 48) / 8))
    cancelled = (~delivered) | (rng.random(N_ORDERS) < .035 * cancel_prob)
    delivered = ~cancelled

    base_price = basket
    surge = 1 + .04 * peak + .07 * (traffic == "High") + .05 * (weather == "Rain")
    price = base_price * surge
    discount = np.where(rng.random(N_ORDERS) < .22, rng.uniform(.05, .25, N_ORDERS), 0)
    revenue = np.where(delivered, price * (1 - discount), 0)

    orders = pd.DataFrame({
        "order_id": np.arange(1, N_ORDERS + 1),
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

    for df, name in [(users, "users"), (restaurants, "restaurants"), (riders, "riders"), (orders, "orders")]:
        df.to_csv(OUT / f"{name}.csv", index=False)

    # Event stream: completed order journeys plus browsing/abandonment sessions.
    # This makes funnel conversion measurable from actual event records.
    order_events = []
    order_session_ids = np.arange(1, N_ORDERS + 1)
    order_base = orders[["order_id", "user_id", "restaurant_id", "order_ts", "traffic"]].copy()
    restaurant_lookup = restaurants.set_index("restaurant_id")["cuisine"]
    order_base["cuisine"] = order_base["restaurant_id"].map(restaurant_lookup)

    for row in order_base.itertuples(index=False):
        base_ts = row.order_ts
        offsets = [(-8, "session_start"), (-6, "menu_view"), (-4, "add_to_cart"), (-2, "checkout"), (0, "order")]
        for minutes, event_name in offsets:
            order_events.append((f"S{row.order_id:07d}", row.user_id, base_ts + pd.Timedelta(minutes=minutes), event_name, row.restaurant_id, row.cuisine, row.traffic))

    browse_user = rng.integers(1, n_users + 1, N_BROWSE_SESSIONS)
    browse_restaurant = rng.integers(1, n_restaurants + 1, N_BROWSE_SESSIONS)
    browse_ts = sample_order_timestamps(N_BROWSE_SESSIONS, start, 180)
    browse_traffic = rng.choice(["Low", "Medium", "High"], N_BROWSE_SESSIONS, p=[.40, .43, .17])
    browse_cuisine = restaurant_lookup.reindex(browse_restaurant).to_numpy()

    menu_ok = rng.random(N_BROWSE_SESSIONS) < .82
    cart_ok = menu_ok & (rng.random(N_BROWSE_SESSIONS) < .55)
    checkout_ok = cart_ok & (rng.random(N_BROWSE_SESSIONS) < .68)

    for i in range(N_BROWSE_SESSIONS):
        sid = f"B{i + 1:07d}"
        stages = [("session_start", 0)]
        if menu_ok[i]:
            stages.append(("menu_view", 3))
        if cart_ok[i]:
            stages.append(("add_to_cart", 6))
        if checkout_ok[i]:
            stages.append(("checkout", 9))
        for event_name, minutes in stages:
            order_events.append((sid, browse_user[i], browse_ts[i] + pd.Timedelta(minutes=minutes), event_name, int(browse_restaurant[i]), browse_cuisine[i], browse_traffic[i]))

    events = pd.DataFrame(order_events, columns=["session_id", "user_id", "event_ts", "event_name", "restaurant_id", "cuisine", "traffic"])
    events.sort_values(["event_ts", "session_id"], inplace=True)
    events.to_csv(OUT / "events.csv", index=False)

    # Synthetic A/B-test dataset for demonstrating a product experimentation workflow.
    exp_n = N_EXPERIMENT_SESSIONS
    exp_session = np.arange(1, exp_n + 1)
    variant = rng.choice(["Control", "Treatment"], exp_n)
    treatment = (variant == "Treatment").astype(int)
    conversion_prob = .118 + .018 * treatment
    converted = rng.random(exp_n) < conversion_prob
    exp_gmv = np.where(converted, np.clip(rng.lognormal(5.15, .50, exp_n), 120, 2500), 0)
    exp_cancelled = converted & (rng.random(exp_n) < (.065 - .010 * treatment))
    experiments = pd.DataFrame({
        "experiment_id": "checkout_redesign_v1",
        "session_id": [f"E{x:07d}" for x in exp_session],
        "variant": variant,
        "converted": converted.astype(int),
        "gmv": exp_gmv.round(2),
        "cancelled": exp_cancelled.astype(int)
    })
    experiments.to_csv(OUT / "experiments.csv", index=False)

    print(f"Generated {len(orders):,} orders, {events.session_id.nunique():,} funnel sessions, and {len(experiments):,} experiment sessions.")


if __name__ == "__main__":
    main()
