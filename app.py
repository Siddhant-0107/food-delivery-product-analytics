import math
import streamlit as st
import pandas as pd
import plotly.express as px
from src.models import load_model
from src.pricing import optimize_price
from src.forecast import forecast_next_24

st.set_page_config(page_title="Food Delivery Product Analytics", page_icon="🍽️", layout="wide")
st.title("🍽️ Food Delivery Product Analytics")
st.caption("Marketplace performance • Customer behavior • Retention • Operations • Pricing")
orders = pd.read_csv("data/orders.csv", parse_dates=["order_ts"])
restaurants = pd.read_csv("data/restaurants.csv")
try: events = pd.read_csv("data/events.csv", parse_dates=["event_ts"])
except FileNotFoundError: events = None
try: experiments = pd.read_csv("data/experiments.csv")
except FileNotFoundError: experiments = None

st.sidebar.header("Analysis filters")
min_date,max_date=orders.order_ts.min().date(),orders.order_ts.max().date()
date_range=st.sidebar.date_input("Order date",(min_date,max_date),min_value=min_date,max_value=max_date)
if isinstance(date_range,(tuple,list)) and len(date_range)==2: start_date,end_date=date_range
else: start_date=end_date=date_range
cuisine=st.sidebar.selectbox("Cuisine",["All"]+sorted(restaurants.cuisine.unique().tolist()))
traffic=st.sidebar.selectbox("Traffic",["All"]+sorted(orders.traffic.unique().tolist()))
filtered=orders[orders.order_ts.dt.date.between(start_date,end_date)].copy()
if traffic!="All": filtered=filtered[filtered.traffic==traffic]
if cuisine!="All":
    filtered=filtered.merge(restaurants[["restaurant_id","cuisine"]],on="restaurant_id",how="inner")
    filtered=filtered[filtered.cuisine==cuisine]
if filtered.empty: st.warning("No orders match the selected filters."); st.stop()

def money(x):
    x=float(x)
    if x>=1_000_000:return f"₹{x/1_000_000:.1f}M"
    if x>=1_000:return f"₹{x/1_000:.1f}K"
    return f"₹{x:,.0f}"

total_orders=len(filtered); delivered=int(filtered.delivered.sum()); cancel_rate=filtered.cancelled.mean()*100
aov=filtered.loc[filtered.delivered==1,"revenue"].mean(); gmv=filtered.loc[filtered.delivered==1,"revenue"].sum()
sla=(filtered.loc[filtered.delivered==1,"eta_minutes"]<=45).mean()*100 if delivered else 0
st.subheader("Marketplace snapshot")
k1,k2,k3,k4,k5,k6=st.columns(6)
k1.metric("Orders",f"{total_orders:,}"); k2.metric("GMV",money(gmv)); k3.metric("AOV",money(aov)); k4.metric("Cancellation",f"{cancel_rate:.1f}%"); k5.metric("Delivery rate",f"{100-cancel_rate:.1f}%"); k6.metric("≤45 min SLA",f"{sla:.1f}%")
st.caption("Decision framework: metric → trend → segmentation → insight → recommendation")
tabs=st.tabs(["Executive KPIs","Funnel & Demand","Restaurant Performance","Customers & Retention","Cancellations & Risk","Pricing & Experiments"])

with tabs[0]:
    st.subheader("Marketplace performance")
    daily=filtered.assign(date=filtered.order_ts.dt.date).groupby("date",as_index=False).agg(orders=("order_id","count"),gmv=("revenue","sum"),cancellation_rate=("cancelled","mean"),avg_eta=("eta_minutes","mean")); daily["cancellation_rate"]*=100
    daily["orders_7d"]=daily.orders.rolling(7,min_periods=1).mean(); daily["gmv_7d"]=daily.gmv.rolling(7,min_periods=1).mean(); daily["cancel_7d"]=daily.cancellation_rate.rolling(7,min_periods=1).mean(); daily["eta_7d"]=daily.avg_eta.rolling(7,min_periods=1).mean()
    a,b=st.columns(2)
    with a: st.plotly_chart(px.line(daily,x="date",y=["orders","orders_7d"],title="Daily orders + 7-day trend"),use_container_width=True)
    with b: st.plotly_chart(px.line(daily,x="date",y=["gmv","gmv_7d"],title="Daily GMV + 7-day trend"),use_container_width=True)
    a,b=st.columns(2)
    with a: st.plotly_chart(px.line(daily,x="date",y=["cancellation_rate","cancel_7d"],title="Cancellation + 7-day trend"),use_container_width=True)
    with b: st.plotly_chart(px.line(daily,x="date",y=["avg_eta","eta_7d"],title="Average ETA + 7-day trend"),use_container_width=True)
    peak=daily.loc[daily.orders.idxmax()]; worst=daily.loc[daily.cancellation_rate.idxmax()]
    x,y=st.columns(2); x.info(f"**Peak demand:** {peak.date} recorded **{int(peak.orders):,} orders**. Rolling trend separates signal from daily noise."); y.warning(f"**Highest cancellation:** {worst.date} reached **{worst.cancellation_rate:.1f}%**. Segment by hour, traffic and restaurant before acting.")

with tabs[1]:
    st.subheader("Funnel & demand")
    if events is not None:
        ev=events[events.event_ts.dt.date.between(start_date,end_date)].copy(); order=["session_start","menu_view","add_to_cart","checkout","order"]
        counts=ev[ev.event_name.isin(order)].groupby("event_name")["session_id"].nunique().reindex(order).fillna(0)
        funnel=pd.DataFrame({"stage":order,"sessions":counts.values}); funnel["conversion"]=funnel.sessions.div(funnel.sessions.shift(1)).fillna(1)*100; funnel["drop_off"]=100-funnel.conversion
        st.plotly_chart(px.funnel(funnel,y="stage",x="sessions",title="Customer journey funnel"),use_container_width=True)
        view=funnel.copy(); view["conversion"]=view.conversion.round(1); view["drop_off"]=view.drop_off.round(1); st.dataframe(view,use_container_width=True,hide_index=True)
        leak=funnel.iloc[1:].sort_values("conversion").iloc[0]; st.info(f"**Largest leakage:** {leak.stage.replace('_',' ').title()} retains **{leak.conversion:.1f}%** of the previous stage. Investigate UX, fee visibility and operational constraints before changing acquisition spend.")
    else: st.warning("Funnel data is missing. Rerun `python generate_data.py` after pulling the latest repository.")
    hourly=filtered.groupby("hour",as_index=False).agg(orders=("order_id","count"),gmv=("revenue","sum")); st.plotly_chart(px.bar(hourly,x="hour",y="orders",title="Orders by hour of day"),use_container_width=True)
    peak_hour=int(hourly.loc[hourly.orders.idxmax(),"hour"]); st.info(f"**Demand signal:** {peak_hour}:00 is the busiest hour. Use this window for capacity planning and controlled promotions.")
    try:
        fc=forecast_next_24(orders); st.plotly_chart(px.line(fc,x="order_ts",y="forecast_orders",markers=True,title="Next 24-hour demand forecast (supporting analysis)"),use_container_width=True)
    except Exception: pass

with tabs[2]:
    st.subheader("Restaurant performance scorecard")
    perf=filtered.merge(restaurants,on="restaurant_id",how="left"); score=perf.groupby(["restaurant_id","cuisine"],as_index=False).agg(orders=("order_id","count"),gmv=("revenue","sum"),cancellation_rate=("cancelled","mean"),avg_eta=("eta_minutes","mean"),rating=("rating","first")); score["cancellation_rate"]*=100; score["status"]="Healthy"; score.loc[(score.cancellation_rate>=score.cancellation_rate.quantile(.9))|(score.avg_eta>=score.avg_eta.quantile(.9)),"status"]="Needs attention"
    st.plotly_chart(px.scatter(score,x="avg_eta",y="gmv",size="orders",color="cuisine",hover_name="restaurant_id",title="GMV vs delivery time"),use_container_width=True)
    display=score.sort_values("gmv",ascending=False).head(30).copy(); display["gmv"]=display.gmv.round(0); display["cancellation_rate"]=display.cancellation_rate.round(1); display["avg_eta"]=display.avg_eta.round(1)
    st.dataframe(display[["restaurant_id","cuisine","orders","gmv","avg_eta","cancellation_rate","rating","status"]],use_container_width=True,hide_index=True); st.info("**Action lens:** prioritize high-volume restaurants with poor ETA or cancellation performance because they create larger marketplace impact.")

with tabs[3]:
    st.subheader("Customers & retention")
    completed=filtered[filtered.delivered==1].copy(); customer=completed.groupby("user_id",as_index=False).agg(orders=("order_id","count"),revenue=("revenue","sum"),last_order=("order_ts","max")); customer["segment"]="Occasional"; customer.loc[customer.orders==1,"segment"]="New / one-time"; customer.loc[(customer.orders>=2)&(customer.orders<=3),"segment"]="Repeat"; customer.loc[(customer.orders>=4)&(customer.revenue>=customer.revenue.median()),"segment"]="Loyal high-value"
    counts=customer.segment.value_counts().reset_index(); counts.columns=["segment","customers"]; st.plotly_chart(px.bar(counts,x="segment",y="customers",title="Behavioral customer segments"),use_container_width=True)
    cohort=completed.assign(cohort=completed.groupby("user_id")["order_ts"].transform("min").dt.to_period("M").astype(str),order_month=completed.order_ts.dt.to_period("M").astype(str)); ct=cohort.groupby(["cohort","order_month"])["user_id"].nunique().reset_index(name="customers"); st.plotly_chart(px.density_heatmap(ct,x="order_month",y="cohort",z="customers",title="Cohort activity heatmap"),use_container_width=True); st.info("**Retention lens:** identify cohorts that retain beyond first purchase and segments that contribute repeat GMV.")

with tabs[4]:
    st.subheader("Cancellation investigation")
    by_hour=filtered.groupby("hour",as_index=False).agg(cancellation_rate=("cancelled","mean"),orders=("order_id","count")); by_hour["cancellation_rate"]*=100; by_traffic=filtered.groupby("traffic",as_index=False).agg(cancellation_rate=("cancelled","mean"),orders=("order_id","count")); by_traffic["cancellation_rate"]*=100
    a,b=st.columns(2)
    with a: st.plotly_chart(px.line(by_hour,x="hour",y="cancellation_rate",markers=True,title="Cancellation rate by hour"),use_container_width=True)
    with b: st.plotly_chart(px.bar(by_traffic,x="traffic",y="cancellation_rate",text_auto=".1f",title="Cancellation rate by traffic"),use_container_width=True)
    worst=by_traffic.loc[by_traffic.cancellation_rate.idxmax()]; st.warning(f"**Investigation lead:** {worst.traffic} traffic has the highest cancellation rate (**{worst.cancellation_rate:.1f}%**). Segment by restaurant, distance and peak hour before recommending a fix.")
    try:
        model=load_model("cancel_model.joblib")
        with st.expander("Optional cancellation-risk simulator"):
            c1,c2,c3=st.columns(3); distance=c1.slider("Distance (km)",.5,14.0,4.0); items=c2.slider("Items",1,6,2); basket=c3.slider("Basket value (₹)",120,2500,600); traffic2=st.selectbox("Traffic",["Low","Medium","High"]); weather=st.selectbox("Weather",["Clear","Cloudy","Rain"]); hour2=st.slider("Order hour",0,23,20); weekend=st.checkbox("Weekend")
            x=pd.DataFrame([{"distance_km":distance,"items":items,"basket_value":basket,"hour":hour2,"weekend":int(weekend),"traffic":{"Low":0,"Medium":1,"High":2}[traffic2],"weather":{"Clear":0,"Cloudy":1,"Rain":2}[weather]}]); risk=float(model.predict_proba(x)[:,1][0]); st.metric("Estimated cancellation risk",f"{risk*100:.1f}%")
    except Exception: pass

with tabs[5]:
    st.subheader("Pricing & experiments"); st.markdown("Evaluate **demand, revenue, contribution margin and customer impact** together.")
    a,b,c=st.columns(3); reference=a.number_input("Current price (₹)",100.0,3000.0,399.0); demand=b.number_input("Baseline demand",1.0,10000.0,350.0); cost=c.number_input("Unit cost (₹)",10.0,2500.0,180.0); result=optimize_price(reference,demand,cost)
    p1,p2,p3,p4=st.columns(4); p1.metric("Recommended price",f"₹{result['recommended_price']:.0f}"); p2.metric("Expected demand",f"{result['expected_demand']:.0f}"); p3.metric("Expected revenue",money(result['expected_revenue'])); p4.metric("Contribution",money(result['expected_contribution']))
    chart=pd.DataFrame({"price":result["price_grid"],"expected_revenue":result["revenue_grid"],"contribution":result["contribution_grid"]}); st.plotly_chart(px.line(chart,x="price",y=["expected_revenue","contribution"],markers=True,title="Revenue vs contribution across feasible prices"),use_container_width=True); st.info("**Pricing guardrail:** recommendation maximizes modeled contribution subject to a minimum margin floor. Validate price changes with randomized treatment/control groups.")
    if experiments is not None:
        st.markdown("### Checkout experiment"); exp=experiments.groupby("variant",as_index=False).agg(sessions=("session_id","count"),conversions=("converted","sum"),gmv=("gmv","sum"),cancellations=("cancelled","sum")); exp["conversion_rate"]=exp.conversions/exp.sessions; exp["cancel_rate"]=exp.cancellations/exp.conversions.replace(0,pd.NA); control=exp[exp.variant=="Control"].iloc[0]; treatment=exp[exp.variant=="Treatment"].iloc[0]; pc,pt=control.conversion_rate,treatment.conversion_rate; pooled=(control.conversions+treatment.conversions)/(control.sessions+treatment.sessions); se=math.sqrt(pooled*(1-pooled)*(1/control.sessions+1/treatment.sessions)); z=(pt-pc)/se if se else 0; cdf=lambda x:0.5*(1+math.erf(x/math.sqrt(2))); pval=2*(1-cdf(abs(z))); lift=(pt/pc-1)*100 if pc else 0
        e1,e2,e3=st.columns(3); e1.metric("Treatment conversion",f"{pt*100:.2f}%",f"{lift:+.1f}% vs control"); e2.metric("p-value",f"{pval:.4f}"); e3.metric("Treatment GMV / session",money(treatment.gmv/treatment.sessions)); st.dataframe(exp.assign(conversion_rate=(exp.conversion_rate*100).round(2),cancel_rate=(exp.cancel_rate*100).round(2)),use_container_width=True,hide_index=True); st.info("**Experiment readout:** conversion is the primary metric; cancellation and GMV are guardrails. Evaluate effect size and customer impact before rollout.")
