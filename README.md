# Food Delivery Product Analytics Platform

> Placement-ready Product Analytics project focused on SQL, product metrics, funnels, cohorts, customer segmentation, restaurant performance, experimentation, and pricing decisions.

## Business Problem

A food-delivery marketplace needs a reliable analytics layer to answer where the customer funnel leaks, which customers drive revenue and retention, which restaurants create poor experiences, when demand peaks, what drives cancellations, and whether pricing or promotions improve business outcomes.

This project simulates an end-to-end product analytics workflow over 250K synthetic orders, turning raw marketplace data into decision-ready KPIs, SQL analysis, dashboards, and recommendations.

## Product questions answered

1. **How is the marketplace performing?** Orders, GMV, AOV, conversion, cancellation and SLA.
2. **Where is the funnel leaking?** Session → menu → cart → checkout → order conversion.
3. **Which customers matter most?** RFM segments, new vs returning behavior and cohort retention.
4. **Which restaurants need intervention?** Volume, acceptance, preparation time, SLA and cancellation scorecards.
5. **When does demand peak?** Hour/day and operational demand patterns.
6. **What happens if pricing changes?** Demand, revenue and margin trade-offs.
7. **How should a product team measure a change?** A/B-testing style analysis with primary and guardrail metrics.

## Analytics stack

- **Python + Pandas** for data generation and transformations
- **SQL + DuckDB** for analytics and KPI computation
- **Streamlit + Plotly** for the product dashboard
- **FastAPI** for supporting decision APIs
- **pytest + GitHub Actions** for quality checks
- **scikit-learn** only as a supporting decision layer

The main project story is **Business question → Metric → SQL/Analysis → Insight → Recommendation → Measurement**.

## Dashboard

The dashboard is organized around product decisions rather than model types:

- Executive KPIs
- Funnel & Demand
- Restaurant Performance
- Customers & Retention
- Cancellations & Risk
- Pricing & Experiments

## Example product investigation

**Cancellation rate increases.**

Do not jump straight to a solution. Segment the change by restaurant, hour, geography, customer type, preparation time and delivery time. Identify the largest contributing segment, formulate competing hypotheses, validate them with SQL or experimentation, and recommend an intervention. Monitor cancellation rate alongside completed orders, SLA, rating and retention as guardrails.

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

- Built an end-to-end product analytics platform over **250K synthetic food-delivery orders**, defining marketplace KPIs including GMV, AOV, conversion, cancellation, SLA and retention.
- Developed SQL-driven **funnel, cohort, RFM, customer, restaurant and demand analyses** to identify product and operational opportunities.
- Built an interactive dashboard to translate marketplace data into **customer, restaurant, demand and pricing insights**, with decision-oriented recommendations and guardrail metrics.
- Added experimentation and pricing analysis to evaluate **conversion, demand, revenue and margin trade-offs**, using predictive models only as supporting decision tools.

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
