import sys
from pathlib import Path

import pandas as pd

# Make the repository root importable when pytest is launched from any directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pricing import demand_multiplier, optimize_price


def test_demand_falls_when_price_rises():
    assert demand_multiplier(120, 100) < demand_multiplier(100, 100)


def test_optimizer_respects_margin_floor():
    result = optimize_price(100, 100, 90, min_margin=0.20)
    assert result["recommended_price"] >= 90 / 0.8


def test_kpi_rates_from_order_level_data():
    orders = pd.DataFrame(
        {
            "cancelled": [0, 1, 0, 0],
            "delivered": [1, 0, 1, 1],
            "eta_minutes": [35, 60, 42, 51],
            "revenue": [300, 0, 500, 400],
        }
    )
    assert orders["cancelled"].mean() * 100 == 25.0
    assert orders["delivered"].mean() * 100 == 75.0
    delivered = orders[orders["delivered"] == 1]
    assert (delivered["eta_minutes"] <= 45).mean() * 100 == 2 / 3 * 100


def test_funnel_stage_conversion_is_adjacent_stage_rate():
    stages = pd.Series(
        [1000, 800, 440, 300, 240],
        index=["session_start", "menu_view", "add_to_cart", "checkout", "order"],
        dtype=float,
    )
    conversion = stages.div(stages.shift(1)).fillna(1) * 100
    assert conversion["menu_view"] == 80.0
    assert round(conversion["add_to_cart"], 10) == 55.0
    assert conversion["order"] == 80.0


def test_percentage_point_delta_for_rates():
    current = 5.8
    previous = 6.4
    assert round(current - previous, 1) == -0.6
