# Product Analyst Interview Guide

## 60-second project pitch

"I built a food-delivery product intelligence platform to simulate how a product analytics team would work with marketplace data. I generated 250K orders and built a DuckDB analytics layer with SQL for core KPIs, funnel analysis, customer cohorts and RFM segmentation, restaurant performance, cancellations, and demand. I then exposed the analysis through a Streamlit dashboard and added pricing/experimentation decision support. The main focus is not prediction; it is turning product data into measurable business decisions."

## Metrics to know

### Funnel
- Sessions
- Menu-view rate
- Cart conversion
- Checkout conversion
- Order conversion

### Marketplace
- Orders
- GMV
- AOV
- Cancellation rate
- Acceptance rate
- SLA/on-time rate

### Customer
- Repeat purchase rate
- Retention
- Cohort retention
- LTV

### Guardrails
- Refund rate
- Cancellation rate
- Delivery SLA
- Customer rating
- Contribution margin

## Investigation framework

When a metric moves:

1. Validate the metric definition.
2. Check whether the movement is real or a data issue.
3. Compare against a historical baseline.
4. Segment by time, geography, customer, restaurant, and platform.
5. Identify the largest contributing segment.
6. Form competing hypotheses.
7. Test them with SQL or experimentation.
8. Recommend an action.
9. Define success and guardrail metrics.

## Example case

**Cancellation rate rises from 8% to 11%.**

Do not immediately conclude why. Break it down by restaurant, hour, city/zone, new vs returning users, delivery time, preparation time, and order value. Determine whether the increase is concentrated in one operational segment. Quantify its contribution and recommend an intervention. Measure success using cancellation rate plus completed orders, SLA, customer rating, and retention.

## SQL questions this project prepares you for

- Top-N restaurants by GMV
- Week-over-week growth
- Customers with 3+ orders
- First-order cohorts
- Retention by cohort
- Cancellation rate by restaurant
- Rolling 7-day order volume
- Funnel conversion
- Percent contribution to GMV

## A/B testing

Know:

- Control vs treatment
- Primary metric
- Secondary metrics
- Guardrail metrics
- Statistical significance
- Sample size / power
- Practical significance
- Novelty effects
- Segment-level analysis

## Product sense

Always connect analysis to an action.

Weak:
> "Conversion dropped 5%."

Strong:
> "Checkout conversion dropped 5%, concentrated on Android users after the payment-step change. I would validate payment failures, compare against the control or previous version, and monitor successful payments and cancellation as guardrails before rolling back or fixing the experience."
