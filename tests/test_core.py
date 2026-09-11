from src.pricing import demand_multiplier, optimize_price

def test_demand_falls_when_price_rises():
    assert demand_multiplier(120, 100) < demand_multiplier(100, 100)

def test_optimizer_respects_margin_floor():
    result = optimize_price(100, 100, 90, min_margin=.20)
    assert result["recommended_price"] >= 90 / .8
