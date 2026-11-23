import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="NovaSphere Sales Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp {background: linear-gradient(180deg, #F5F7FB 0%, #EEF2F7 100%);}
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1450px;}
    h1, h2, h3 {color: #12213A;}
    div[data-testid="stMetric"] {
        background: white; border: 1px solid #E6EAF0; padding: 18px 20px;
        border-radius: 16px; box-shadow: 0 7px 22px rgba(26, 45, 82, 0.07);
    }
    div[data-testid="stMetricLabel"] {color: #586A84; font-weight: 600;}
    div[data-testid="stMetricValue"] {color: #12213A; font-weight: 800;}
    section[data-testid="stSidebar"] {background: #12213A;}
    section[data-testid="stSidebar"] * {color: #F7F9FC;}
    .dashboard-header {
        padding: 22px 26px; border-radius: 18px; color: white; margin-bottom: 18px;
        background: linear-gradient(110deg, #12213A, #2855A6 62%, #20A4A0);
        box-shadow: 0 10px 30px rgba(18, 33, 58, 0.18);
    }
    .dashboard-header h1 {color: white; margin: 0; font-size: 2rem;}
    .dashboard-header p {margin: 7px 0 0 0; color: #DDE8FF;}
    .section-title {font-size: 1.13rem; font-weight: 750; color: #12213A; margin: 10px 0 4px;}
</style>
""", unsafe_allow_html=True)

COLOR_SEQUENCE = ["#2855A6", "#20A4A0", "#F59E0B", "#8B5CF6", "#EF5B5B", "#4F86C6", "#34A853"]

@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "fictional_sales_data.csv"
    data = pd.read_csv(file_path)
    data["Order_Date"] = pd.to_datetime(data["Order_Date"], errors="coerce")
    numeric_cols = ["Units_Sold", "Unit_Price", "Discount_Rate", "Sales", "Cost", "Profit"]
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    return data.dropna(subset=["Order_Date"])

df = load_data()

st.markdown("""
<div class="dashboard-header">
  <h1>NovaSphere Sales Intelligence</h1>
  <p>Interactive performance dashboard for a fictional global sales company</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Dashboard Filters")
    min_date = df["Order_Date"].min().date()
    max_date = df["Order_Date"].max().date()
    selected_dates = st.date_input("Order date", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    selected_regions = st.multiselect("Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))
    selected_categories = st.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))
    selected_segments = st.multiselect("Customer segment", sorted(df["Customer_Segment"].unique()), default=sorted(df["Customer_Segment"].unique()))
    selected_channels = st.multiselect("Sales channel", sorted(df["Sales_Channel"].unique()), default=sorted(df["Sales_Channel"].unique()))
    st.caption("Tip: clear a selection to temporarily exclude that dimension.")

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])
else:
    start_date, end_date = df["Order_Date"].min(), df["Order_Date"].max()

filtered = df[
    df["Order_Date"].between(start_date, end_date)
    & df["Region"].isin(selected_regions)
    & df["Category"].isin(selected_categories)
    & df["Customer_Segment"].isin(selected_segments)
    & df["Sales_Channel"].isin(selected_channels)
].copy()

if filtered.empty:
    st.warning("No sales records match the selected filters. Please broaden your selections.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
orders = filtered["Order_ID"].nunique()
units = int(filtered["Units_Sold"].sum())
margin = total_profit / total_sales if total_sales else 0
avg_order = total_sales / orders if orders else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Sales", f"${total_sales:,.0f}")
k2.metric("Total Profit", f"${total_profit:,.0f}")
k3.metric("Profit Margin", f"{margin:.1%}")
k4.metric("Orders", f"{orders:,}")
k5.metric("Average Order", f"${avg_order:,.0f}")

st.markdown('<div class="section-title">Sales trend and product mix</div>', unsafe_allow_html=True)
left, right = st.columns([1.7, 1])

monthly = (filtered.set_index("Order_Date").resample("MS").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index())
fig_time = go.Figure()
fig_time.add_trace(go.Scatter(x=monthly["Order_Date"], y=monthly["Sales"], name="Sales", mode="lines+markers", line=dict(color="#2855A6", width=3), fill="tozeroy", fillcolor="rgba(40,85,166,0.10)"))
fig_time.add_trace(go.Scatter(x=monthly["Order_Date"], y=monthly["Profit"], name="Profit", mode="lines+markers", line=dict(color="#20A4A0", width=3)))
fig_time.update_layout(title="Monthly sales and profit", height=390, margin=dict(l=10, r=10, t=55, b=10), hovermode="x unified", legend=dict(orientation="h", y=1.12), plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
fig_time.update_yaxes(tickprefix="$", tickformat=",.0f", gridcolor="#E9EDF3")
left.plotly_chart(fig_time, use_container_width=True)

category = filtered.groupby("Category", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
fig_pie = px.pie(category, names="Category", values="Sales", hole=0.58, title="Sales by category", color_discrete_sequence=COLOR_SEQUENCE)
fig_pie.update_traces(textposition="inside", textinfo="percent+label", hovertemplate="%{label}<br>$%{value:,.0f}<br>%{percent}<extra></extra>")
fig_pie.update_layout(height=390, margin=dict(l=10, r=10, t=55, b=10), showlegend=False, paper_bgcolor="rgba(0,0,0,0)")
right.plotly_chart(fig_pie, use_container_width=True)

st.markdown('<div class="section-title">Geographic performance</div>', unsafe_allow_html=True)
g1, g2 = st.columns(2)
region_sales = filtered.groupby("Region", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).sort_values("Sales")
fig_region = px.bar(region_sales, x="Sales", y="Region", orientation="h", color="Sales", color_continuous_scale=["#CFE1FF", "#2855A6"], title="Sales by region", text_auto="$.3s")
fig_region.update_layout(height=390, margin=dict(l=10, r=10, t=55, b=10), coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
fig_region.update_xaxes(tickprefix="$", tickformat=",.0f", gridcolor="#E9EDF3")
g1.plotly_chart(fig_region, use_container_width=True)

country_sales = filtered.groupby(["Country", "Region"], as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).nlargest(12, "Sales").sort_values("Sales")
fig_country = px.bar(country_sales, x="Sales", y="Country", orientation="h", color="Region", title="Top countries by sales", text_auto="$.3s", color_discrete_sequence=COLOR_SEQUENCE)
fig_country.update_layout(height=390, margin=dict(l=10, r=10, t=55, b=10), legend=dict(orientation="h", y=1.15), plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
fig_country.update_xaxes(tickprefix="$", tickformat=",.0f", gridcolor="#E9EDF3")
g2.plotly_chart(fig_country, use_container_width=True)

st.markdown('<div class="section-title">Commercial drivers</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
product_sales = filtered.groupby("Product", as_index=False)["Sales"].sum().nlargest(10, "Sales").sort_values("Sales")
fig_product = px.bar(product_sales, x="Sales", y="Product", orientation="h", title="Top 10 products", color="Sales", color_continuous_scale=["#C9F0EA", "#168B87"], text_auto="$.3s")
fig_product.update_layout(height=420, margin=dict(l=10, r=10, t=55, b=10), coloraxis_showscale=False, plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
fig_product.update_xaxes(tickprefix="$", tickformat=",.0f", gridcolor="#E9EDF3")
c1.plotly_chart(fig_product, use_container_width=True)

channel = filtered.groupby("Sales_Channel", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
channel_long = channel.melt(id_vars="Sales_Channel", value_vars=["Sales", "Profit"], var_name="Metric", value_name="Amount")
fig_channel = px.bar(channel_long, x="Sales_Channel", y="Amount", color="Metric", barmode="group", title="Sales and profit by channel", color_discrete_map={"Sales": "#2855A6", "Profit": "#20A4A0"}, text_auto="$.3s")
fig_channel.update_layout(height=420, margin=dict(l=10, r=10, t=55, b=10), plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
fig_channel.update_yaxes(tickprefix="$", tickformat=",.0f", gridcolor="#E9EDF3")
c2.plotly_chart(fig_channel, use_container_width=True)

with st.expander("View and download filtered sales records"):
    display_cols = ["Order_ID", "Order_Date", "Region", "Country", "Category", "Product", "Sales_Channel", "Customer_Segment", "Units_Sold", "Sales", "Profit"]
    table_data = filtered[display_cols].sort_values("Order_Date", ascending=False).copy()
    table_data["Order_Date"] = table_data["Order_Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(table_data, use_container_width=True, hide_index=True, column_config={"Sales": st.column_config.NumberColumn(format="$%.2f"), "Profit": st.column_config.NumberColumn(format="$%.2f")})
    st.download_button("Download filtered CSV", data=filtered.to_csv(index=False).encode("utf-8"), file_name="filtered_sales_data.csv", mime="text/csv")

st.caption(f"Showing {len(filtered):,} of {len(df):,} fictional sales records • {units:,} units sold")
