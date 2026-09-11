import math
from datetime import timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from src.models import load_model
from src.pricing import optimize_price

st.set_page_config(
    page_title="Food Delivery Product Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {max-width: 1500px; padding-top: 1.2rem; padding-bottom: 2rem;}
    h1 {letter-spacing: -0.03em; margin-bottom: 0.15rem;}
    .subtitle {color:#667085; font-size:0.95rem; margin-bottom:1.2rem;}
    .section-note {color:#667085; font-size:0.82rem; margin-top:-0.35rem; margin-bottom:0.8rem;}
    div[data-testid="stMetric"] {padding: 0.75rem 0.9rem; border:1px solid #eaecf0; border-radius:12px; background:#fff;}
    div[data-testid="stMetricLabel"] {font-size:0.76rem;}
    div[data-testid="stMetricValue"] {font-size:1.45rem;}
    .insight {padding:0.8rem 1rem; border:1px solid #eaecf0; border-radius:10px; background:#f8fafc; min-height:82px;}
    .insight-title {font-weight:700; font-size:0.86rem; margin-bottom:0.25rem;}
    .insight-text {font-size:0.80rem; color:#475467; line-height:1.45;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🍽️ Food Delivery Product Analytics")
st.markdown(
    '<div class="subtitle">Marketplace performance • Customer behavior • Retention • Operations • Pricing</div>',
    unsafe_allow_html=True,
)

orders = pd.read_csv("data/orders.csv", parse_dates=["order_ts"])
restaurants = pd.read_csv("data/restaurants.csv")
try:
    events = pd.read_csv("data/events.csv", parse_dates=["event_ts"])
except FileNotFoundError:
    events = None
try:
    experiments = pd.read_csv("data/experiments.csv")
except FileNotFoundError:
    experiments = None

st.sidebar.header("Analysis controls")
min_date = orders.order_ts.min().date()
max_date = orders.order_ts.max().date()

period = st.sidebar.selectbox(
    "Analysis period",
    ["Last 30 days", "Last 90 days", "Full period", "Custom"],
    index=0,
)
if period == "Last 30 days":
    start_date, end_date = max(min_date, max_date - timedelta(days=29)), max_date
elif period == "Last 90 days":
    start_date, end_date = max(min_date, max_date - timedelta(days=89)), max_date
elif period == "Full period":
    start_date, end_date = min_date, max_date
else:
    selected = st.sidebar.date_input(
        "Order date",
        (max(min_date, max_date - timedelta(days=29)), max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(selected, (tuple, list)) and len(selected) == 2:
        start_date, end_date = selected
    else:
        start_date = end_date = selected

cuisine = st.sidebar.selectbox("Cuisine", ["All"] + sorted(restaurants.cuisine.unique().tolist()))
traffic = st.sidebar.selectbox("Traffic", ["All"] + sorted(orders.traffic.unique().tolist()))

filtered = orders[orders.order_ts.dt.date.between(start_date, end_date)].copy()
if traffic != "All":
    filtered = filtered[filtered.traffic == traffic]
if cuisine != "All":
    filtered = filtered.merge(
        restaurants[["restaurant_id", "cuisine"]], on="restaurant_id", how="inner", suffixes=("", "_restaurant")
    )
    filtered = filtered[filtered.cuisine == cuisine]

if filtered.empty:
    st.warning("No orders match the selected filters.")
    st.stop()


def money(value):
    value = float(value)
    if value >= 1_000_000:
        return f"₹{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"₹{value / 1_000:.1f}K"
    return f"₹{value:,.0f}"


def pct(value):
    return f"{float(value):.1f}%"


def period_metrics(df):
    delivered_df = df[df.delivered == 1]
    return {
        "orders": len(df),
        "gmv": delivered_df.revenue.sum(),
        "aov": delivered_df.revenue.mean() if not delivered_df.empty else 0,
        "cancel": df.cancelled.mean() * 100,
        "delivery": df.delivered.mean() * 100,
        "sla": (delivered_df.eta_minutes <= 45).mean() * 100 if not delivered_df.empty else 0,
    }


current = period_metrics(filtered)
period_days = (end_date - start_date).days + 1
previous_end = start_date - timedelta(days=1)
previous_start = previous_end - timedelta(days=period_days - 1)
previous = orders[orders.order_ts.dt.date.between(previous_start, previous_end)].copy()
if traffic != "All":
    previous = previous[previous.traffic == traffic]
if cuisine != "All":
    previous = previous.merge(restaurants[["restaurant_id", "cuisine"]], on="restaurant_id", how="inner")
    previous = previous[previous.cuisine == cuisine]
prev = period_metrics(previous) if not previous.empty else None


def delta(key):
    if not prev or prev[key] == 0:
        return None
    return (current[key] / prev[key] - 1) * 100


def pp_delta(key):
    if not prev:
        return None
    return current[key] - prev[key]


st.caption(f"Showing {start_date:%d %b %Y} – {end_date:%d %b %Y}  •  Previous period: {previous_start:%d %b} – {previous_end:%d %b %Y}")
st.subheader("Marketplace snapshot")

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Orders", f"{current['orders']:,}", f"{delta('orders'):+.1f}%" if delta('orders') is not None else None)
k2.metric("GMV", money(current["gmv"]), f"{delta('gmv'):+.1f}%" if delta('gmv') is not None else None)
k3.metric("AOV", money(current["aov"]), f"{delta('aov'):+.1f}%" if delta('aov') is not None else None)
k4.metric("Cancellation", pct(current["cancel"]), f"{pp_delta('cancel'):+.2f} pp" if pp_delta('cancel') is not None else None, delta_color="inverse")
k5.metric("Delivery rate", pct(current["delivery"]), f"{pp_delta('delivery'):+.2f} pp" if pp_delta('delivery') is not None else None)
k6.metric("≤45 min SLA", pct(current["sla"]), f"{pp_delta('sla'):+.2f} pp" if pp_delta('sla') is not None else None)

st.caption("Decision framework: metric → trend → segmentation → insight → recommendation")
tabs = st.tabs([
    "Executive KPIs",
    "Funnel & Demand",
    "Restaurant Performance",
    "Customers & Retention",
    "Cancellations & Risk",
    "Pricing & Experiments",
])

with tabs[0]:
    st.subheader("Marketplace performance")
    st.markdown('<div class="section-note">Track volume, monetization and service quality without mixing unrelated scales.</div>', unsafe_allow_html=True)

    daily = (
        filtered.assign(date=filtered.order_ts.dt.date)
        .groupby("date", as_index=False)
        .agg(
            orders=("order_id", "count"),
            gmv=("revenue", "sum"),
            cancellation_rate=("cancelled", "mean"),
            avg_eta=("eta_minutes", "mean"),
        )
    )
    daily["cancellation_rate"] *= 100
    daily["orders_7d"] = daily.orders.rolling(7, min_periods=1).mean()
    daily["gmv_7d"] = daily.gmv.rolling(7, min_periods=1).mean()
    daily["cancel_7d"] = daily.cancellation_rate.rolling(7, min_periods=1).mean()
    daily["eta_7d"] = daily.avg_eta.rolling(7, min_periods=1).mean()

    a, b = st.columns(2)
    with a:
        fig = px.line(daily, x="date", y=["orders", "orders_7d"], title="Daily orders")
        fig.update_layout(height=300, legend_title_text="")
        fig.update_yaxes(title_text="Orders")
        fig.for_each_trace(lambda trace: trace.update(name="Daily orders" if trace.name == "orders" else "7-day average"))
        st.plotly_chart(fig, use_container_width=True)
    with b:
        fig = px.line(daily, x="date", y=["gmv", "gmv_7d"], title="Daily GMV")
        fig.update_layout(height=300, legend_title_text="")
        fig.update_yaxes(title_text="GMV (₹)", tickprefix="₹", tickformat=",.0f")
        fig.for_each_trace(lambda trace: trace.update(name="Daily GMV" if trace.name == "gmv" else "7-day average"))
        st.plotly_chart(fig, use_container_width=True)

    a, b = st.columns(2)
    with a:
        fig = px.line(daily, x="date", y=["cancellation_rate", "cancel_7d"], title="Cancellation rate")
        fig.update_layout(height=300, legend_title_text="")
        fig.update_yaxes(title_text="Cancellation rate (%)")
        fig.for_each_trace(lambda trace: trace.update(name="Daily cancellation rate" if trace.name == "cancellation_rate" else "7-day average"))
        st.plotly_chart(fig, use_container_width=True)
    with b:
        fig = px.line(daily, x="date", y=["avg_eta", "eta_7d"], title="Average ETA")
        fig.update_layout(height=300, legend_title_text="")
        fig.update_yaxes(title_text="ETA (min)")
        fig.for_each_trace(lambda trace: trace.update(name="Daily ETA" if trace.name == "avg_eta" else "7-day average"))
        st.plotly_chart(fig, use_container_width=True)

    peak = daily.loc[daily.orders.idxmax()]
    worst = daily.loc[daily.cancellation_rate.idxmax()]
    i1, i2 = st.columns(2)
    with i1:
        st.markdown(
            f'<div class="insight"><div class="insight-title">Peak demand</div><div class="insight-text">{peak.date} recorded <b>{int(peak.orders):,} orders</b>. Use the peak window for capacity planning and controlled promotions.</div></div>',
            unsafe_allow_html=True,
        )
    with i2:
        st.markdown(
            f'<div class="insight"><div class="insight-title">Service risk</div><div class="insight-text">Cancellation peaked at <b>{worst.cancellation_rate:.1f}%</b> on {worst.date}. Segment by traffic, restaurant and distance before acting.</div></div>',
            unsafe_allow_html=True,
        )

with tabs[1]:
    st.subheader("Funnel & demand")
    st.markdown('<div class="section-note">Identify where sessions leak before spending more on acquisition.</div>', unsafe_allow_html=True)

    if events is not None:
        ev = events[events.event_ts.dt.date.between(start_date, end_date)].copy()
        if traffic != "All":
            ev = ev[ev.traffic == traffic]
        if cuisine != "All":
            ev = ev[ev.cuisine == cuisine]

        stages = ["session_start", "menu_view", "add_to_cart", "checkout", "order"]
        stage_labels = {
            "session_start": "Session start",
            "menu_view": "Menu view",
            "add_to_cart": "Add to cart",
            "checkout": "Checkout",
            "order": "Order",
        }
        counts = (
            ev[ev.event_name.isin(stages)]
            .groupby("event_name")["session_id"]
            .nunique()
            .reindex(stages)
            .fillna(0)
        )
        funnel = pd.DataFrame({"stage": stages, "sessions": counts.values})
        funnel["stage_label"] = funnel["stage"].map(stage_labels)
        funnel["conversion"] = funnel.sessions.div(funnel.sessions.shift(1)).fillna(1) * 100
        funnel["drop_off"] = 100 - funnel.conversion
        funnel["overall_conversion"] = funnel.sessions.div(funnel.sessions.iloc[0]) * 100

        fig = px.funnel(funnel, y="stage_label", x="sessions", title="Customer journey funnel")
        fig.update_layout(height=360)
        fig.update_yaxes(title_text="Stage")
        fig.update_xaxes(title_text="Sessions")
        st.plotly_chart(fig, use_container_width=True)

        view = funnel.copy()
        view["conversion"] = view.conversion.round(1)
        view["drop_off"] = view.drop_off.round(1)
        view["overall_conversion"] = view.overall_conversion.round(1)
        view["stage"] = view["stage_label"]
        view = view[["stage", "sessions", "conversion", "drop_off", "overall_conversion"]]
        view.columns = ["Stage", "Sessions", "Stage conversion %", "Drop-off %", "Overall conversion %"]
        st.dataframe(view, use_container_width=True, hide_index=True)

        leak = funnel.iloc[1:].sort_values("conversion").iloc[0]
        st.info(
            f"**Largest leakage:** {leak.stage_label} retains **{leak.conversion:.1f}%** of the previous stage. Investigate UX, fee visibility and availability before changing acquisition spend."
        )
    else:
        st.warning("Funnel data is missing. Run `python generate_data.py` after pulling the latest repository.")

    hourly = filtered.groupby("hour", as_index=False).agg(orders=("order_id", "count"), gmv=("revenue", "sum"))
    fig = px.bar(hourly, x="hour", y="orders", title="Orders by hour of day")
    fig.update_layout(height=300)
    fig.update_xaxes(title_text="Hour of day")
    fig.update_yaxes(title_text="Orders")
    st.plotly_chart(fig, use_container_width=True)
    peak_hour = int(hourly.loc[hourly.orders.idxmax(), "hour"])
    peak_orders = int(hourly.loc[hourly.orders.idxmax(), "orders"])
    st.info(f"**Demand signal:** {peak_hour:02d}:00 is the busiest hour with **{peak_orders:,} orders**. Prioritize rider and restaurant capacity during this peak window.")

with tabs[2]:
    st.subheader("Restaurant performance scorecard")
    st.markdown('<div class="section-note">Prioritize high-volume restaurants where operational issues have the largest marketplace impact.</div>', unsafe_allow_html=True)

    perf = filtered.merge(restaurants, on="restaurant_id", how="left", suffixes=("", "_restaurant"))
    score = (
        perf.groupby(["restaurant_id", "cuisine"], as_index=False)
        .agg(
            orders=("order_id", "count"),
            gmv=("revenue", "sum"),
            cancellation_rate=("cancelled", "mean"),
            avg_eta=("eta_minutes", "mean"),
            rating=("rating", "first"),
        )
    )
    score["cancellation_rate"] *= 100
    score["status"] = "Healthy"
    score.loc[
        (score.cancellation_rate >= score.cancellation_rate.quantile(0.9))
        | (score.avg_eta >= score.avg_eta.quantile(0.9)),
        "status",
    ] = "Needs attention"

    fig = px.scatter(
        score,
        x="avg_eta",
        y="gmv",
        size="orders",
        color="status",
        hover_name="restaurant_id",
        title="GMV vs delivery time",
    )
    fig.update_layout(height=380)
    fig.update_xaxes(title_text="Average ETA (min)")
    fig.update_yaxes(title_text="GMV (₹)", tickprefix="₹", tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    display = score.sort_values("gmv", ascending=False).head(30).copy()
    display["gmv"] = display.gmv.round(0)
    display["cancellation_rate"] = display.cancellation_rate.round(1)
    display["avg_eta"] = display.avg_eta.round(1)
    st.dataframe(
        display[["restaurant_id", "cuisine", "orders", "gmv", "avg_eta", "cancellation_rate", "rating", "status"]],
        use_container_width=True,
        hide_index=True,
    )

with tabs[3]:
    st.subheader("Customers & retention")
    st.markdown('<div class="section-note">Separate one-time users from repeat and high-value customers to guide retention investment.</div>', unsafe_allow_html=True)

    completed = filtered[filtered.delivered == 1].copy()
    customer = (
        completed.groupby("user_id", as_index=False)
        .agg(orders=("order_id", "count"), revenue=("revenue", "sum"), last_order=("order_ts", "max"))
    )
    customer["segment"] = "Occasional"
    customer.loc[customer.orders == 1, "segment"] = "New / one-time"
    customer.loc[(customer.orders >= 2) & (customer.orders <= 3), "segment"] = "Repeat"
    customer.loc[(customer.orders >= 4) & (customer.revenue >= customer.revenue.median()), "segment"] = "Loyal high-value"

    counts = customer.segment.value_counts().reset_index()
    counts.columns = ["segment", "customers"]
    fig = px.bar(counts, x="segment", y="customers", title="Behavioral customer segments")
    fig.update_layout(height=320)
    fig.update_xaxes(title_text="Customer segment")
    fig.update_yaxes(title_text="Customers")
    st.plotly_chart(fig, use_container_width=True)

    cohort = completed.assign(
        cohort=completed.groupby("user_id")["order_ts"].transform("min").dt.to_period("M").astype(str),
        order_month=completed.order_ts.dt.to_period("M").astype(str),
    )
    ct = cohort.groupby(["cohort", "order_month"])["user_id"].nunique().reset_index(name="customers")
    fig = px.density_heatmap(ct, x="order_month", y="cohort", z="customers", title="Cohort activity heatmap")
    fig.update_layout(height=420)
    fig.update_xaxes(title_text="Order month")
    fig.update_yaxes(title_text="Cohort month")
    st.plotly_chart(fig, use_container_width=True)
    st.info("**Retention lens:** focus on cohorts that generate repeat purchases and segments that contribute disproportionate repeat GMV.")

with tabs[4]:
    st.subheader("Cancellation investigation")
    st.markdown('<div class="section-note">Treat cancellation as an investigation problem: isolate the operational driver before recommending an intervention.</div>', unsafe_allow_html=True)

    by_hour = filtered.groupby("hour", as_index=False).agg(cancellation_rate=("cancelled", "mean"), orders=("order_id", "count"))
    by_hour["cancellation_rate"] *= 100
    by_traffic = filtered.groupby("traffic", as_index=False).agg(cancellation_rate=("cancelled", "mean"), orders=("order_id", "count"))
    by_traffic["cancellation_rate"] *= 100

    a, b = st.columns(2)
    with a:
        fig = px.line(by_hour, x="hour", y="cancellation_rate", markers=True, title="Cancellation rate by hour")
        fig.update_layout(height=300)
        fig.update_xaxes(title_text="Hour of day")
        fig.update_yaxes(title_text="Cancellation rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    with b:
        fig = px.bar(by_traffic, x="traffic", y="cancellation_rate", text_auto=".1f", title="Cancellation rate by traffic")
        fig.update_layout(height=300)
        fig.update_xaxes(title_text="Traffic")
        fig.update_yaxes(title_text="Cancellation rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    worst = by_traffic.loc[by_traffic.cancellation_rate.idxmax()]
    st.warning(
        f"**Investigation lead:** {worst.traffic} traffic has the highest cancellation rate (**{worst.cancellation_rate:.1f}%**). Segment by restaurant, distance and peak hour before recommending a fix."
    )

    try:
        model = load_model("cancel_model.joblib")
        with st.expander("Optional cancellation-risk simulator"):
            c1, c2, c3 = st.columns(3)
            distance = c1.slider("Distance (km)", 0.5, 14.0, 4.0)
            items = c2.slider("Items", 1, 6, 2)
            basket = c3.slider("Basket value (₹)", 120, 2500, 600)
            traffic2 = st.selectbox("Traffic", ["Low", "Medium", "High"])
            weather = st.selectbox("Weather", ["Clear", "Cloudy", "Rain"])
            hour2 = st.slider("Order hour", 0, 23, 20)
            weekend = st.checkbox("Weekend")
            x = pd.DataFrame([
                {
                    "distance_km": distance,
                    "items": items,
                    "basket_value": basket,
                    "hour": hour2,
                    "weekend": int(weekend),
                    "traffic": {"Low": 0, "Medium": 1, "High": 2}[traffic2],
                    "weather": {"Clear": 0, "Cloudy": 1, "Rain": 2}[weather],
                }
            ])
            risk = float(model.predict_proba(x)[:, 1][0])
            st.metric("Estimated cancellation risk", f"{risk * 100:.1f}%")
    except Exception:
        pass

with tabs[5]:
    st.subheader("Pricing & experiments")
    st.markdown('<div class="section-note">Evaluate revenue, contribution margin and customer impact together; do not optimize price on revenue alone.</div>', unsafe_allow_html=True)

    a, b, c = st.columns(3)
    reference = a.number_input("Current price (₹)", 100.0, 3000.0, 399.0)
    demand = b.number_input("Baseline demand", 1.0, 10000.0, 350.0)
    cost = c.number_input("Unit cost (₹)", 10.0, 2500.0, 180.0)
    result = optimize_price(reference, demand, cost)

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Recommended price", f"₹{result['recommended_price']:.0f}")
    p2.metric("Expected demand", f"{result['expected_demand']:.0f}")
    p3.metric("Expected revenue", money(result["expected_revenue"]))
    p4.metric("Contribution", money(result["expected_contribution"]))

    chart = pd.DataFrame(
        {
            "price": result["price_grid"],
            "expected_revenue": result["revenue_grid"],
            "contribution": result["contribution_grid"],
        }
    )
    fig = px.line(chart, x="price", y=["expected_revenue", "contribution"], markers=True, title="Revenue vs contribution across feasible prices")
    fig.update_layout(height=340, legend_title_text="")
    fig.update_xaxes(title_text="Price (₹)")
    fig.update_yaxes(title_text="Value (₹)", tickprefix="₹", tickformat=",.0f")
    fig.for_each_trace(lambda trace: trace.update(name="Expected revenue" if trace.name == "expected_revenue" else "Contribution"))
    st.plotly_chart(fig, use_container_width=True)
    st.info("**Pricing guardrail:** maximize modeled contribution subject to the margin floor, then validate any price change with randomized treatment/control groups.")

    if experiments is not None:
        st.markdown("### Checkout experiment")
        exp = experiments.groupby("variant", as_index=False).agg(
            sessions=("session_id", "count"),
            conversions=("converted", "sum"),
            gmv=("gmv", "sum"),
            cancellations=("cancelled", "sum"),
        )
        exp["conversion_rate"] = exp.conversions / exp.sessions
        exp["cancel_rate"] = exp.cancellations / exp.conversions.replace(0, pd.NA)

        if set(exp.variant) >= {"Control", "Treatment"}:
            control = exp[exp.variant == "Control"].iloc[0]
            treatment = exp[exp.variant == "Treatment"].iloc[0]
            pc, pt = control.conversion_rate, treatment.conversion_rate
            pooled = (control.conversions + treatment.conversions) / (control.sessions + treatment.sessions)
            se = math.sqrt(pooled * (1 - pooled) * (1 / control.sessions + 1 / treatment.sessions))
            z = (pt - pc) / se if se else 0
            cdf = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
            pval = 2 * (1 - cdf(abs(z)))
            lift = (pt / pc - 1) * 100 if pc else 0
            gmv_per_session = treatment.gmv / treatment.sessions

            e1, e2, e3 = st.columns(3)
            e1.metric("Treatment conversion", f"{pt * 100:.2f}%", f"{lift:+.1f}% vs control")
            e2.metric("Statistical significance", "p < 0.0001" if pval < 0.0001 else f"p = {pval:.4f}")
            e3.metric("Treatment GMV / session", money(gmv_per_session))

            decision = "Strong evidence to test rollout" if pval < 0.05 and lift > 0 else "Do not roll out yet"
            if pval < 0.05 and lift > 0:
                st.success(f"**Experiment decision:** {decision}. Treatment improves the primary conversion metric; verify guardrails before scaling.")
            else:
                st.warning(f"**Experiment decision:** {decision}. Conversion lift is not sufficiently supported by this test.")

            display_exp = exp.copy()
            display_exp["conversion_rate"] = (display_exp.conversion_rate * 100).round(2)
            display_exp["cancel_rate"] = (display_exp.cancel_rate * 100).round(2)
            display_exp.columns = ["Variant", "Sessions", "Conversions", "GMV", "Cancellations", "Conversion %", "Cancel %"]
            st.dataframe(display_exp, use_container_width=True, hide_index=True)
            st.caption("Primary metric: checkout conversion. Guardrails: cancellation rate and GMV per session.")
