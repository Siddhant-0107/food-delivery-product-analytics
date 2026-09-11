import streamlit as st
import pandas as pd
import plotly.express as px
from src.analytics import query
from src.models import load_model
from src.pricing import optimize_price
from src.forecast import forecast_next_24

st.set_page_config(page_title="Food Delivery Intelligence", layout="wide")
st.title("🍽️ Food Delivery Intelligence")
st.caption("Product analytics decision support: KPIs • funnel • retention • restaurant performance • demand • pricing")
st.caption("Product analytics • ML risk prediction • demand intelligence • pricing simulation")

orders = pd.read_csv("data/orders.csv")
restaurants = pd.read_csv("data/restaurants.csv")

kpi = query(open("sql/kpis.sql").read()).iloc[0]
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Orders", f"{int(kpi.orders):,}")
c2.metric("Delivery rate", f"{kpi.delivery_rate_pct:.1f}%")
c3.metric("Cancellation", f"{kpi.cancellation_rate_pct:.1f}%")
c4.metric("Avg ETA", f"{kpi.avg_eta_minutes:.1f} min")
c5.metric("Revenue", f"₹{kpi.total_revenue:,.0f}")

tabs = st.tabs(["Executive KPIs","Funnel & Demand","Restaurant Performance","Customers & Retention","Cancellations & Risk","Pricing & Experiments"])

with tabs[0]:
    daily = orders.assign(date=pd.to_datetime(orders.order_ts).dt.date).groupby("date",as_index=False).agg(
        orders=("order_id","count"), revenue=("revenue","sum"), eta=("eta_minutes","mean"))
    st.plotly_chart(px.line(daily, x="date", y=["orders","revenue"], title="Daily orders and revenue"), use_container_width=True)
    st.plotly_chart(px.line(daily, x="date", y="eta", title="Average ETA"), use_container_width=True)

with tabs[1]:
    hourly = orders.groupby("hour",as_index=False).agg(orders=("order_id","count"), revenue=("revenue","sum"))
    st.plotly_chart(px.bar(hourly, x="hour", y="orders", title="Order demand by hour"), use_container_width=True)
    forecast = forecast_next_24(orders)
    st.plotly_chart(px.line(forecast, x="order_ts", y="forecast_orders", markers=True, title="Next 24-hour demand forecast"), use_container_width=True)
    st.dataframe(hourly, use_container_width=True)

with tabs[2]:
    perf = query(open("sql/restaurant_performance.sql").read())
    st.plotly_chart(px.scatter(perf, x="avg_eta", y="revenue", size="orders", color="cuisine",
                               hover_name="restaurant_id", title="Restaurant revenue vs delivery speed"),
                    use_container_width=True)
    st.dataframe(perf.head(30), use_container_width=True)

with tabs[3]:
    seg = query(open("sql/customer_segments.sql").read())
    counts = seg.segment.value_counts().reset_index()
    counts.columns = ["segment","customers"]
    st.plotly_chart(px.bar(counts, x="segment", y="customers", title="Customer segments"), use_container_width=True)
    st.dataframe(seg.sort_values("monetary", ascending=False).head(50), use_container_width=True)

with tabs[4]:
    model = load_model("cancel_model.joblib")
    st.subheader("Cancellation-risk simulator")
    col1,col2,col3 = st.columns(3)
    distance = col1.slider("Distance (km)", .5, 14.0, 4.0)
    items = col2.slider("Items", 1, 6, 2)
    basket = col3.slider("Basket value (₹)", 120, 2500, 600)
    traffic = st.selectbox("Traffic", ["Low","Medium","High"])
    weather = st.selectbox("Weather", ["Clear","Cloudy","Rain"])
    hour = st.slider("Order hour", 0, 23, 20)
    weekend = st.checkbox("Weekend")
    x = pd.DataFrame([{
        "distance_km":distance,"items":items,"basket_value":basket,"hour":hour,
        "weekend":int(weekend),"traffic":{"Low":0,"Medium":1,"High":2}[traffic],
        "weather":{"Clear":0,"Cloudy":1,"Rain":2}[weather]
    }])
    risk = float(model.predict_proba(x)[:,1][0])
    st.metric("Predicted cancellation risk", f"{risk*100:.1f}%")

with tabs[5]:
    st.subheader("Revenue-maximizing what-if pricing")
    a,b,c = st.columns(3)
    reference = a.number_input("Current price (₹)", 100.0, 3000.0, 399.0)
    demand = b.number_input("Estimated baseline demand", 1.0, 10000.0, 350.0)
    cost = c.number_input("Unit cost (₹)", 10.0, 2500.0, 180.0)
    result = optimize_price(reference, demand, cost)
    st.metric("Recommended price", f"₹{result['recommended_price']:.0f}")
    st.metric("Expected demand", f"{result['expected_demand']:.0f}")
    st.metric("Expected revenue", f"₹{result['expected_revenue']:,.0f}")
    chart = pd.DataFrame({"price":result["price_grid"],"expected_revenue":result["revenue_grid"]})
    st.plotly_chart(px.line(chart, x="price", y="expected_revenue", markers=True,
                            title="Revenue across feasible prices"), use_container_width=True)
    st.info("This is a simulation using an explicit elasticity assumption; it is not a causal estimate.")
