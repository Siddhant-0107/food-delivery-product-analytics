# Food Delivery Product Intelligence Platform

> **Placement-ready Product Analytics project** focused on SQL, product metrics, funnels, cohorts, customer segmentation, restaurant performance, experimentation, and pricing decisions.

## Business Problem

A food-delivery marketplace has thousands of customers, restaurants, orders, and delivery events. Product and operations teams need a reliable way to answer:

- Where is the customer funnel leaking?
- Which customer segments drive revenue and retention?
- Which restaurants create poor customer experiences?
- When and where does demand peak?
- What is driving cancellations?
- Do discounts and pricing changes improve business outcomes?
- Which product or operational actions should the team prioritize?

This project builds an end-to-end **product analytics layer** that turns raw order/event data into decision-ready KPIs, SQL analyses, dashboards, and recommendations.

## What this project demonstrates

### 1. Product KPI framework
Core metrics include:

- Orders
- GMV
- Average Order Value (AOV)
- Conversion rate
- Cancellation rate
- On-time delivery / SLA rate
- Repeat purchase rate
- Customer retention
- Restaurant acceptance rate

### 2. Funnel analysis

The dashboard breaks the customer journey into:

`Sessions → Menu Views → Cart → Checkout → Orders`

The goal is to identify the largest drop-offs and quantify the potential impact of improving each stage.

### 3. Customer analytics

Customers are segmented using behavioral and monetary signals:

- Recency
- Frequency
- Monetary value
- New vs returning users
- Cohort retention

This supports targeted retention and reactivation strategies rather than treating every customer identically.

### 4. Restaurant performance

Restaurants are evaluated across:

- Order volume
- Acceptance rate
- Preparation time
- Delivery SLA
- Cancellation rate
- Customer experience

This creates an operational scorecard that can be used to identify restaurants requiring intervention.

### 5. Demand intelligence

Orders are analyzed by:

- Hour of day
- Day of week
- Peak vs non-peak periods
- Restaurant/category
- Location

This helps answer questions such as when additional delivery capacity or promotional activity may be needed.

### 6. Pricing & promotion analysis

Instead of treating pricing as an ML problem, the project frames pricing as a **business decision**:

`Price / Discount → Demand → Revenue → Margin → Customer impact`

A lightweight elasticity simulation is included to evaluate pricing scenarios and their potential trade-offs.

### 7. Experimentation

The project includes an A/B-test style analysis framework for comparing product variants.

Example questions:

- Did a checkout change improve conversion?
- Did a promotion increase orders enough to justify its cost?
- Did a new delivery fee reduce completed orders?

The emphasis is on **incremental impact and statistical significance**, not simply comparing averages.

## Technology

**Primary Product Analytics stack**

- Python
- Pandas
- SQL
- DuckDB
- Streamlit
- Plotly

**Supporting**

- scikit-learn
- FastAPI
- Docker
- pytest
- GitHub Actions

Machine learning is intentionally kept as a **supporting component** for decision support rather than the central focus.

## Architecture

```text
                 ┌────────────────────┐
                 │ Synthetic Event /  │
                 │ Order Data         │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Python ETL +       │
                 │ Data Preparation   │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ DuckDB             │
                 │ Analytics Layer    │
                 └─────────┬──────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
       KPI / Funnel    Customers      Restaurants
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                 ┌────────────────────┐
                 │ Product Dashboard  │
                 │ + Decision Support │
                 └────────────────────┘
```

## Repository structure

```text
food-delivery-intelligence/
├── app.py
├── generate_data.py
├── run_pipeline.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── README.md
├── src/
│   ├── analytics.py
│   ├── models.py
│   └── pricing.py
├── sql/
│   ├── kpis.sql
│   ├── restaurant_performance.sql
│   ├── customer_segments.sql
│   └── cohort_retention.sql
└── tests/
    └── test_core.py
```

## Running locally

```bash
pip install -r requirements.txt
python generate_data.py
python run_pipeline.py
streamlit run app.py
```

The dashboard is organized around product questions rather than model types:

1. Executive
2. Funnel & Demand
3. Restaurants
4. Customers
5. Risk
6. Pricing & Experiments

## Example interview discussion

### Product sense
**Question:** Cancellation rate increased.

A strong investigation would segment the change by:

`restaurant × hour × location × customer type × preparation time × delivery time`

Then determine whether the increase is caused primarily by supply/restaurant issues, delivery delays, customer behavior, or a change in the product funnel.

### SQL
Typical analyses include:

- Daily/weekly KPI trends
- Top and bottom restaurants
- Customer cohorts
- Repeat-purchase behavior
- RFM segmentation
- Cancellation breakdowns
- Funnel conversion

### Business recommendation

The output should not stop at:

> "Restaurant X has a high cancellation rate."

It should progress to:

> "Restaurant X contributes disproportionately to cancellations during the evening peak. Prioritize operational intervention during this window; measure success using cancellation rate, SLA rate, completed orders, and customer retention."

## Resume-ready description

**Food Delivery Product Intelligence Platform** | Python, SQL, DuckDB, Streamlit, Plotly

- Built an end-to-end product analytics platform over **250K synthetic food-delivery orders**, defining and tracking KPIs including GMV, AOV, conversion, cancellations, SLA, and retention.
- Developed SQL-based **funnel, cohort, RFM, customer, restaurant, and demand analyses** to identify product and operational opportunities.
- Built an interactive Streamlit dashboard for **customer segmentation, restaurant scorecards, demand patterns, cancellation drivers, and pricing scenarios**, translating analysis into actionable business recommendations.
- Added an experimentation/pricing analysis layer to evaluate **conversion, demand, revenue, and margin trade-offs**, with predictive models used only as supporting decision tools.

## Interview talking points

Be prepared to explain:

1. Why each KPI was chosen.
2. How you would define an order, active customer, repeat customer, and retention.
3. How you would design the funnel.
4. How you would investigate a sudden conversion drop.
5. How cohort retention differs from repeat purchase rate.
6. How you would identify a problematic restaurant.
7. How you would distinguish correlation from causation.
8. How you would design an A/B test.
9. Which guardrail metrics you would monitor.
10. How a pricing change can increase revenue but still hurt customers or long-term retention.

## Important positioning

This is **not intended to be presented as a machine-learning project**.

The primary story is:

**Business question → Metric → SQL/Analysis → Insight → Recommendation → Measurement**

ML/prediction is secondary and exists only where it can improve decision support.

## License

MIT
