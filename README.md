# Food Delivery Product Analytics Platform

> Placement-ready Product Analytics project focused on SQL, product metrics, event funnels, cohorts, customer segmentation, restaurant performance, experimentation, and pricing decisions.

## Business Problem

A food-delivery marketplace needs a reliable analytics layer to answer where the customer funnel leaks, which customers drive revenue and retention, which restaurants create poor experiences, when demand peaks, what drives cancellations, and whether pricing or product changes improve business outcomes.

This project simulates an end-to-end product analytics workflow over **250K synthetic orders**, an event-level customer journey, and an A/B-test dataset, turning raw marketplace data into decision-ready KPIs, SQL analysis, dashboards, and recommendations.

## Product questions answered

1. **How is the marketplace performing?** Orders, GMV, AOV, cancellation and SLA.
2. **Where is the funnel leaking?** Session → menu → cart → checkout → order conversion from event records.
3. **Which customers matter most?** Behavioral segments and cohort retention.
4. **Which restaurants need intervention?** Volume, ETA, rating and cancellation scorecards.
5. **When does demand peak?** Hour/day demand patterns with rolling trends and supporting forecast analysis.
6. **What happens if pricing changes?** Demand, revenue and contribution-margin trade-offs.
7. **How should a product team measure a change?** Randomized experiment readout with conversion as primary metric and cancellation/GMV as guardrails.

## Analytics stack

- **Python + Pandas** for synthetic data generation and transformations
- **SQL + DuckDB** for analytics and KPI computation
- **Streamlit + Plotly** for the decision dashboard
- **FastAPI** for supporting decision APIs
- **pytest + GitHub Actions** for quality checks
- **scikit-learn** only as a supporting decision layer

The main project story is **Business question → Metric → SQL/Analysis → Insight → Recommendation → Measurement**.

## Generated datasets

Running `python generate_data.py` creates:

- `users.csv` — 30K customers and acquisition channels
- `restaurants.csv` — 900 restaurants, cuisines, ratings and capacity
- `riders.csv` — 700 delivery partners
- `orders.csv` — 250K marketplace orders with demand peaks, traffic, weather, ETA, cancellations, discounts and revenue
- `events.csv` — session-level `session_start → menu_view → add_to_cart → checkout → order` journeys plus abandonment sessions
- `experiments.csv` — synthetic Control/Treatment checkout experiment with conversion, GMV and cancellation outcomes

The event stream is used directly by the dashboard funnel; funnel numbers are not hard-coded.

## Dashboard

The dashboard is organized around product decisions rather than model types:

- Executive KPIs — daily metrics plus 7-day rolling trends
- Funnel & Demand — event funnel, conversion/drop-off, hourly demand and forecast
- Restaurant Performance — GMV, ETA, cancellations and operational scorecard
- Customers & Retention — behavioral segments and cohorts
- Cancellations & Risk — root-cause investigation with optional supporting risk model
- Pricing & Experiments — contribution-margin pricing simulator and A/B-test readout

## Pricing and experimentation

The pricing simulator maximizes modeled contribution subject to a minimum margin floor rather than optimizing revenue alone. The dashboard explicitly labels the simulator as directional and recommends randomized testing for causal validation.

The checkout experiment reports treatment conversion, relative lift, a two-proportion z-test p-value, GMV/session and cancellation guardrails. The experiment is synthetic and exists to demonstrate the analysis workflow.

## Repository structure

```text
.
├── app.py
├── api.py
├── generate_data.py
├── run_pipeline.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── README.md
├── PRODUCT_ANALYST_INTERVIEW.md
├── src/
│   ├── __init__.py
│   ├── analytics.py
│   ├── forecast.py
│   ├── models.py
│   └── pricing.py
├── sql/
│   ├── kpis.sql
│   ├── restaurant_performance.sql
│   ├── customer_segments.sql
│   ├── cohort_retention.sql
│   └── product_analytics.sql
└── tests/
    └── test_core.py
```

## Run locally

```bash
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python generate_data.py
python run_pipeline.py
python -m streamlit run app.py
```

## Placement-ready resume bullets

**Food Delivery Product Analytics Platform** | Python, SQL, DuckDB, Streamlit, Plotly

- Built an end-to-end product analytics platform over **250K synthetic food-delivery orders and event-level customer journeys**, defining marketplace KPIs including GMV, AOV, cancellation, SLA and retention.
- Developed SQL-driven **funnel, cohort, customer, restaurant and demand analyses** to identify product and operational opportunities.
- Built an interactive decision dashboard with **7-day trends, event funnel conversion, customer segmentation, restaurant scorecards and cancellation investigations**.
- Added a contribution-margin pricing simulator and **A/B-test readout with statistical significance and guardrail metrics**, using predictive models only as supporting decision tools.

## Interview framework

When a metric moves:

1. Validate the metric definition.
2. Check data quality and the historical baseline.
3. Segment by time, geography, customer and supply-side dimensions.
4. Identify the largest contributor.
5. Form and test competing hypotheses.
6. Recommend an action.
7. Define success and guardrail metrics.

See `PRODUCT_ANALYST_INTERVIEW.md` for the interview pitch, metrics, SQL cases, A/B testing and product-sense framework.

## License

MIT
