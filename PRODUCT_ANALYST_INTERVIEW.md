# Food Delivery Product Analytics — Interview Guide

This guide is designed to help you **understand and defend the project in a Product Analyst interview**, not memorize isolated answers.

The project story is:

> **Business question → Metric → Data/SQL → Segmentation → Insight → Recommendation → Measurement**

---

# 1. 60-Second Project Pitch

> “I built a food-delivery product analytics platform to simulate how a product analytics team would work with marketplace data. I generated 250K synthetic orders plus event-level customer journeys and an A/B-test dataset. I used SQL with DuckDB and Python to analyze marketplace KPIs, the customer funnel, cohorts and behavioral segments, restaurant performance, cancellations, demand patterns, pricing trade-offs and experimentation. I then built a Streamlit dashboard so the analysis could be explored interactively. The main focus was not prediction; it was translating product data into measurable business decisions and recommendations.”

### If they ask: “What exactly did you own?”

> “I designed the analytics workflow, defined the metrics, generated the synthetic data, implemented the SQL and Python analysis, built the dashboard and translated the findings into product recommendations and experiment measures.”

---

# 2. Project Architecture

Know what each layer does.

| Layer | Purpose |
|---|---|
| Synthetic data | Simulates users, restaurants, riders, orders, events and experiments |
| Python + Pandas | Data generation and transformations |
| DuckDB + SQL | KPI and analytical queries |
| Streamlit + Plotly | Decision dashboard and exploration |
| Pricing layer | Contribution-margin pricing simulation |
| Experiment layer | Treatment/control readout with statistical testing |
| Supporting model | Optional cancellation/risk signal, not the main story |
| pytest + GitHub Actions | Quality checks |

The important point is that the **analytics layer drives the dashboard**. Funnel numbers are derived from event records rather than manually typed into the UI.

---

# 3. Business Problem

### Question
**Why does a food-delivery marketplace need this analysis?**

### Strong answer
> “A marketplace needs to understand both sides of the product: customer demand and supply-side operations. I wanted to identify where the customer journey leaks, which customers drive revenue and retention, which restaurants create poor experiences, when demand peaks, why cancellations happen, and whether pricing or product changes improve outcomes.”

### Follow-up
**Why is this a product analytics problem rather than just a BI dashboard?**

> “Because I connect the metrics to product decisions. I’m not only reporting orders or GMV. I’m asking where conversion is lost, which user or restaurant segments contribute most to a problem, what intervention should be tested, and how success should be measured.”

---

# 4. Marketplace Metrics

## Orders

Number of orders in the selected period.

## GMV

Gross merchandise value represented here by delivered-order revenue.

### Follow-up: Why not simply sum revenue for every order?

> “Because cancelled orders should not be treated as completed marketplace value. For the dashboard snapshot, GMV is based on delivered orders.”

## AOV

Average order value among delivered orders.

> **AOV = delivered-order revenue / delivered orders**

## Cancellation rate

> **Cancelled orders / total orders**

## Delivery rate

> **Delivered orders / total orders**

## SLA / on-time rate

The dashboard uses the share of delivered orders completed within the defined ETA threshold of **45 minutes**.

### Important interview distinction
Do not call every metric a “revenue metric.” Orders measure volume, GMV measures monetary value, AOV measures value per completed order, while cancellation and SLA measure service quality.

---

# 5. Period-over-Period Comparisons

The dashboard compares the selected period with the immediately preceding period of the same length.

### Question
**Why compare against the previous period?**

> “Absolute values are difficult to interpret without a baseline. A period-over-period comparison shows whether the metric is improving or deteriorating relative to recent performance.”

### Follow-up
**What could make a previous-period comparison misleading?**

> “Seasonality, holidays, unusual events, changes in traffic mix, or incomplete data. For a real product, I would also consider year-over-year or matched historical periods where appropriate.”

---

# 6. Funnel Analysis

The customer journey modeled in the project is:

**Session start → Menu view → Add to cart → Checkout → Order**

### Question
**How do you calculate funnel conversion?**

> “For each stage, I count unique sessions reaching that stage and divide by the count at the previous stage. I also calculate overall conversion from session start to order.”

### Important distinction

**Stage conversion:**
> Current stage sessions / previous stage sessions

**Overall conversion:**
> Current stage sessions / session-start sessions

### Question
**Why use event data rather than order data for the funnel?**

> “Order data only tells me who completed an order. Event data lets me observe the journey before conversion and identify exactly where users abandon.”

### Follow-up
**What would you do after finding the largest drop-off?**

> “First validate that the event instrumentation is correct. Then segment the drop-off by platform, traffic source, cuisine, user type or other relevant dimensions and form hypotheses about the cause before recommending a product change.”

### Possible hypotheses

- Fees become visible too late.
- Restaurant availability is weak.
- Payment friction causes checkout abandonment.
- Delivery estimates are unattractive.
- The page is slow or confusing.
- A specific device/platform has a technical issue.

Never jump directly from **drop-off → cause** without investigation.

---

# 7. Customer Analytics

The project looks at customer behavior using:

- Behavioral segments
- Cohort retention
- Repeat purchase behavior
- Customer value

### Question
**Why segment customers?**

> “Because the average customer hides meaningful differences. A new customer, a high-frequency loyal customer and a declining customer should not receive the same product or retention strategy.”

### Question
**What would you do with a high-value but declining customer?**

> “Prioritize retention. I would identify when the behavior changed, understand the likely friction or reason for decline, and test a targeted intervention rather than sending the same promotion to the whole base.”

---

# 8. Cohort Retention

### Question
**What is a cohort?**

> “A cohort groups users by a common starting event, typically the date or week of first purchase, so we can compare retention among users acquired at different times.”

### Question
**Why are cohorts better than a single retention number?**

> “A single retention rate can mix customers acquired at very different times. Cohorts show whether newer customer groups are behaving better or worse than older groups and whether retention is changing over time.”

### Follow-up
**What would you investigate if recent cohorts have lower retention?**

> “I would compare acquisition source, first-order experience, restaurant availability, delivery experience, discounts, platform and geography, then identify where the decline is concentrated.”

---

# 9. Restaurant Performance

The project builds a restaurant scorecard using:

- Orders
- GMV
- Cancellation rate
- Average ETA
- Rating

### Question
**Why is a restaurant scorecard useful?**

> “Restaurants affect both customer experience and marketplace economics. A high-volume restaurant with poor ETA or cancellation performance can have much larger impact than a low-volume restaurant with the same problem.”

### Key product insight

Do not prioritize restaurants only by **bad rate**.

Consider:

> **Issue severity × business impact**

A restaurant with a high cancellation rate but only a handful of orders may matter less than a high-volume restaurant with a moderately elevated rate.

### Question
**What would you do with a high-volume, poor-performing restaurant?**

> “Quantify its contribution to marketplace cancellations and poor SLA, investigate the operational driver, work with the restaurant or operations team on an intervention, and monitor the relevant metrics after the change.”

---

# 10. Demand & Peak Analysis

The dashboard examines demand by:

- Day
- Hour
- Rolling 7-day trends

### Question
**Why use a 7-day rolling average?**

> “Daily metrics can be noisy. A rolling average smooths short-term fluctuations so the underlying direction is easier to see.”

### Question
**What would you do with a predictable peak-demand window?**

> “Plan rider and restaurant capacity, monitor SLA and cancellation risk, and consider controlled promotions only if operational capacity can support additional demand.”

### Strong product thinking

Never say:

> “Demand peaks, so launch a promotion.”

Instead:

> “Demand peaks, so first ensure supply capacity and service levels can absorb additional volume. Then test whether incremental demand creates profitable completed orders.”

---

# 11. Cancellation Analysis

Suppose:

> **Cancellation rate rises from 8% to 11%.**

Do not immediately claim the cause.

### Investigation framework

1. Validate the metric definition.
2. Check for instrumentation/data-quality changes.
3. Compare with the historical baseline.
4. Break the problem down by restaurant, hour, zone, traffic, customer type, order value and operational variables.
5. Identify the largest contributor.
6. Form competing hypotheses.
7. Quantify the opportunity.
8. Recommend an intervention.
9. Define success and guardrails.

### Example answer

> “I would first confirm that the increase is real and not a data issue. Then I’d segment cancellations by restaurant, time, traffic, delivery time and customer type. If the increase is concentrated in high-volume restaurants during peak hours, I’d investigate capacity or preparation delays. I’d then quantify how much of the marketplace increase is explained by that segment and test an operational intervention while monitoring completed orders, SLA and customer rating as guardrails.”

---

# 12. Risk Model — How to Talk About It

The repository includes a supporting risk-model layer.

### Important
Do **not** make the model the center of your project pitch.

The project's main story is product analytics. The model is a supporting decision layer.

### Question
**Why didn't you make this an ML project?**

> “Because the main business questions were diagnostic and decision-oriented. I used analytics to understand what is happening and why, and treated the model as optional decision support rather than replacing product reasoning with prediction.”

### Question
**How would you evaluate a cancellation model?**

> “I’d consider discrimination metrics such as ROC-AUC or precision/recall depending on the use case, but also calibration, operational usefulness, false-positive cost and whether acting on the predictions actually improves the target business metric.”

---

# 13. Pricing Simulator

The simulator is designed around **contribution margin**, not revenue alone.

### Question
**Why optimize contribution margin instead of revenue?**

> “Because a price can increase revenue while reducing profitability. I want the optimization to respect a minimum margin floor and capture the trade-off between demand and economics.”

### Critical caveat

The simulator is **directional**, not causal.

### Question
**Can you deploy the simulator's recommended price directly?**

> “No. I would treat it as a hypothesis-generating tool and validate pricing changes with randomized experimentation.”

---

# 14. A/B Testing

The project includes a synthetic checkout experiment with Control and Treatment.

Know these terms:

### Control
Baseline experience.

### Treatment
New experience.

### Primary metric
The main metric used to determine whether the change achieved its intended outcome.

For this project, **conversion** is the primary metric.

### Guardrails
Metrics that should not deteriorate materially.

Examples in this project:

- Cancellation rate
- GMV
- Contribution margin
- Delivery SLA
- Customer rating

### Question
**Why not optimize only conversion?**

> “Because conversion can improve while business or customer outcomes get worse. For example, a flow could create more orders but also more cancellations. That is why I use guardrails.”

---

# 15. Statistical Significance

The experiment readout includes a **two-proportion z-test p-value** for conversion.

### Question
**What does the p-value tell you?**

> “It measures how compatible the observed conversion difference is with the null hypothesis of no treatment effect, under the assumptions of the test.”

### Do not say
> “A low p-value proves the treatment works.”

### Better
> “A statistically significant result provides evidence against the null hypothesis, but I would still consider effect size, confidence intervals, practical significance and guardrail impact before shipping.”

---

# 16. Practical vs Statistical Significance

### Question
**A result is statistically significant. Would you launch it?**

> “Not automatically. I would look at the magnitude of the lift, confidence interval, business value, implementation cost and guardrails. A tiny improvement may be statistically significant but not worth shipping.”

### Question
**The result is not statistically significant. Is the feature useless?**

> “Not necessarily. It could be underpowered or the true effect could be small. I would inspect confidence intervals and statistical power before concluding that there is no meaningful effect.”

---

# 17. Sample Size and Power

Know the concepts:

- Baseline conversion
- Minimum detectable effect
- Significance level
- Statistical power
- Sample size

### Question
**Why calculate sample size before an experiment?**

> “To make sure the experiment has enough observations to detect the effect size that matters to the business. Otherwise we risk running an inconclusive test and wasting traffic.”

---

# 18. Segment-Level Experiment Analysis

### Question
**Would you immediately analyze treatment effect for dozens of segments?**

> “Not without caution. Segment-level analysis can create multiple-comparison and low-power problems. I’d pre-specify important segments where possible, ensure adequate sample sizes, and treat exploratory subgroup findings as hypotheses unless supported by a properly designed analysis.”

---

# 19. Dashboard Design

### Question
**Why did you organize the dashboard into these sections?**

Strong answer:

> “I organized it around decisions rather than technical methods: marketplace health, funnel and demand, restaurant operations, customer retention, cancellations, and pricing and experiments. A product manager should be able to move from the headline KPI to the area of investigation without needing to understand how the analysis was implemented.”

### Dashboard sections

1. Executive KPIs
2. Funnel & Demand
3. Restaurant Performance
4. Customers & Retention
5. Cancellations & Risk
6. Pricing & Experiments

---

# 20. Filters and Analytical Scope

The dashboard supports filters such as:

- Analysis period
- Cuisine
- Traffic

### Question
**Why are filters important?**

> “They allow a product or operations user to move from an aggregate KPI to the segment driving the movement. That supports investigation instead of forcing the user to accept an average.”

### Important distinction
Filtering is not the same as proving causality.

A segment with a worse cancellation rate may be associated with the issue without being its root cause.

---

# 21. SQL Questions You Should Be Ready For

You should be able to explain how you would solve these, even if the exact query isn't memorized.

### Top-N restaurants by GMV

Think:

> `GROUP BY restaurant → SUM(GMV) → ORDER BY DESC → LIMIT N`

### Customers with 3+ orders

Think:

> `GROUP BY customer → COUNT(order_id) → HAVING COUNT(*) >= 3`

### Cancellation rate by restaurant

Think:

> `AVG(cancelled)` grouped by restaurant.

### Funnel conversion

Count unique sessions at each event stage, then compare stages.

### Week-over-week growth

Build weekly aggregates and compare the current week with the prior week.

### Rolling 7-day order volume

Aggregate daily orders, then apply a window function such as:

> `AVG(orders) OVER (... ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`

### Cohort retention

Assign users to a first-order cohort and compare later activity back to that cohort.

### Percent contribution to GMV

> Segment GMV / total GMV

---

# 22. SQL Follow-Up Questions Interviewers May Ask

### WHERE vs HAVING?

> `WHERE` filters rows before aggregation. `HAVING` filters groups after aggregation.

### COUNT(*) vs COUNT(DISTINCT customer_id)?

> `COUNT(*)` counts rows. `COUNT(DISTINCT customer_id)` counts unique customers.

### Why can joins inflate a metric?

> A one-to-many join can duplicate rows, causing sums or counts to be overstated. Always validate grain before aggregating.

### What is grain?

> “The level represented by one row.”

Examples:

- One row per order
- One row per customer
- One row per event

This is one of the most important concepts in analytics interviews.

---

# 23. Product-Sense Framework

When the interviewer asks:

> **“A metric dropped. What do you do?”**

Use this sequence:

### 1. Define
What exactly is the metric and denominator?

### 2. Validate
Could this be a data or instrumentation issue?

### 3. Baseline
How unusual is the movement?

### 4. Segment
Where is the change concentrated?

### 5. Hypothesize
What are the plausible causes?

### 6. Test
Use SQL, logs, experiments or additional data.

### 7. Act
Recommend the smallest credible intervention.

### 8. Measure
Define primary success and guardrail metrics.

---

# 24. Common Product Analytics Cases

## Case: Checkout conversion falls

> “I’d segment by platform, app version, payment method, geography, traffic source and user type. I’d check for payment errors and recent product changes. If the decline is isolated to a new Android version after a checkout release, I’d validate the event instrumentation and payment failures, compare with a control or pre-change baseline, and monitor successful payments and cancellation as guardrails.”

## Case: Orders rise but GMV falls

Possible explanations:

- Lower AOV
- More discounted orders
- More low-value customers
- Product mix shift
- Geography mix shift

The next step is decomposition rather than speculation.

## Case: Retention falls

Break down by:

- Acquisition cohort
- Channel
- Geography
- First-order experience
- Restaurant mix
- Delivery quality
- Discount dependence

## Case: Cancellation rises

Break down by:

- Restaurant
- Hour
- Traffic
- Delivery time
- Preparation time
- Distance
- Customer type

---

# 25. “What Is Your Most Important Finding?”

Do not answer with a random chart observation.

Use this structure:

> **Finding → evidence → business implication → action**

Example:

> “The largest opportunity was a concentrated increase in cancellations rather than a broad marketplace decline. The issue was strongest in a high-volume operational segment, which meant the segment contributed disproportionately to the total movement. I would prioritize that segment for intervention and evaluate success using cancellation reduction, completed orders and service-quality guardrails.”

Replace the generic wording above with the actual finding shown by your dashboard when you have the final project metrics in front of you.

---

# 26. “What Would You Do Next?”

Good answers should move from analysis toward validation.

Possible next steps:

- Instrument missing funnel events.
- Investigate high-contribution cancellation segments.
- Test checkout improvements.
- Test retention interventions by customer segment.
- Improve operational capacity during peak demand.
- Validate pricing recommendations with controlled experiments.
- Compare cohorts by acquisition source.

Avoid saying:

> “I would build a more complicated ML model.”

unless you can clearly explain the business decision it would improve.

---

# 27. Limitations of the Project

Be honest about them.

### Synthetic data

> “The datasets are synthetic, so the distributions and relationships are designed for demonstration rather than claimed as real marketplace behavior.”

### Causal limitations

> “Observational analysis identifies patterns and hypotheses, not causal effects. The pricing simulator in particular needs randomized validation.”

### Simplified operational logic

> “The project approximates marketplace operations rather than modeling the full complexity of real rider dispatch, restaurant preparation and pricing systems.”

### Segment definitions

> “Customer segments are analytical business rules, not universal industry standards.”

These limitations make your answer stronger, not weaker.

---

# 28. Why Synthetic Data?

### Question
**Why didn't you use real food-delivery company data?**

> “I used synthetic data because transactional marketplace datasets are difficult to obtain at sufficient scale and with the required event, operational and experimentation fields. The goal was to demonstrate the analytical workflow while making the assumptions explicit.”

### Follow-up
**What would you validate with real data?**

> “Metric definitions, event instrumentation, seasonality, geography, operational constraints, pricing elasticity, customer behavior and the actual causal drivers behind cancellations and retention.”

---

# 29. How to Defend the Project as Product Analytics

Use this sentence:

> “The project is not just a dashboard. Each analysis starts from a product question, defines the metric, identifies the relevant segment, produces an insight, recommends an action and defines how the action should be measured.”

That is the core story.

---

# 30. Mistakes to Avoid in the Interview

### Don't say:

> “The data proves the cause.”

Say:

> “The data indicates a pattern that I would investigate further.”

### Don't say:

> “Statistically significant means successful.”

Say:

> “It provides evidence of a difference; I still need to assess effect size, practical value and guardrails.”

### Don't say:

> “The model predicts cancellations, so we should act on everyone.”

Say:

> “The model is a supporting signal; I would validate whether intervention based on it improves the business outcome.”

### Don't say:

> “Revenue increased, so the product improved.”

Say:

> “Revenue increased; I would decompose the movement into volume, AOV, customer mix and operational quality before deciding whether the product improved.”

---

# 31. Fast Facts to Memorize

Know these without looking at the repo:

- **250K** synthetic orders
- **30K** customers
- **900** restaurants
- **700** riders
- Event funnel: **session → menu → cart → checkout → order**
- Primary experiment metric: **conversion**
- Key experiment guardrails: **GMV and cancellation**, plus business-quality measures such as SLA/rating where relevant
- Pricing objective: **contribution margin with a minimum margin floor**
- Main analytical stack: **Python, SQL, DuckDB, Streamlit, Plotly**
- Core investigation framework: **define → validate → baseline → segment → hypothesize → test → act → measure**

---

# 32. Final Interview Answer Pattern

For almost any project question, use:

> **Context → Metric → Analysis → Insight → Action → Measurement**

Example:

> “We saw cancellation increase. I first validated the metric and compared it with the prior baseline. I segmented the increase by restaurant, time and operational variables and identified where the movement was concentrated. That suggested a capacity or preparation issue rather than a broad demand problem. I would test an operational intervention in the affected segment and measure cancellation reduction, completed orders and SLA as guardrails.”

That is the level of reasoning an interviewer is looking for.
