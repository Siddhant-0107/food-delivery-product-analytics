import numpy as np

def demand_multiplier(price, reference_price, elasticity=-1.15):
    ratio = np.maximum(price / reference_price, .05)
    return ratio ** elasticity

def optimize_price(reference_price, base_demand, unit_cost, min_margin=.20, max_change=.20):
    low = reference_price * (1-max_change)
    high = reference_price * (1+max_change)
    prices = np.linspace(low, high, 41)
    floor = unit_cost / (1-min_margin)
    feasible = prices[prices >= floor]
    if len(feasible) == 0:
        feasible = np.array([floor])
    demand = base_demand * demand_multiplier(feasible, reference_price)
    revenue = feasible * demand
    i = int(np.argmax(revenue))
    return {
        "recommended_price": float(feasible[i]),
        "expected_demand": float(demand[i]),
        "expected_revenue": float(revenue[i]),
        "price_grid": feasible,
        "revenue_grid": revenue
    }
