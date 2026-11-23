import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="NovaSphere Sales Dashboard", page_icon="📊", layout="wide")

UNHCR_BLUE = "#0072BC"
UNHCR_DARK = "#005A8B"
UNHCR_LIGHT = "#EAF6FC"
UNHCR_SKY = "#59C3E6"
UNHCR_NAVY = "#003B5C"
GRID = "#DCEAF2"
COLOR_SEQUENCE = [UNHCR_BLUE, UNHCR_DARK, UNHCR_SKY, "#80D4EE", UNHCR_NAVY, "#A9DFF1", "#2B8CC4"]

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #F7FBFE 0%, #EAF4FA 100%); }
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1450px; }
h1,h2,h3 { color:#003B5C; }
div[data-testid="stMetric"] { background:#FFFFFF; border:1px solid #CFE4F0; padding:18px 20px; border-radius:15px; box-shadow:0 6px 18px rgba(0,90,139,.08); }
div[data-testid="stMetricLabel"] { color:#466879; font-weight:600; }
div[data-testid="stMetricValue"] { color:#005A8B; font-weight:800; }
section[data-testid="stSidebar"] { background:#005A8B; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p { color:#FFFFFF !important; }
.dashboard-header { padding:22px 26px; border-radius:18px; color:white; margin-bottom:18px; background:linear-gradient(110deg,#003B5C,#005A8B 42%,#0072BC 78%,#59C3E6); box-shadow:0 10px 30px rgba(0,90,139,.20); }
.dashboard-header h1 { color:white; margin:0; font-size:2rem; }
.dashboard-header p { margin:7px 0 0; color:#EAF6FC; }
.section-title { font-size:1.13rem; font-weight:750; color:#003B5C; margin:14px 0 7px; }
div[data-testid="stPlotlyChart"] { background:#FFFFFF; border:1px solid #CFE4F0; border-radius:15px; padding:8px; overflow:hidden; box-shadow:0 5px 18px rgba(0,90,139,.06); }
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="input"] > div { background:#FFFFFF !important; border-color:#8CC9E8 !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] span,
section[data-testid="stSidebar"] div[data-baseweb="select"] input,
section[data-testid="stSidebar"] div[data-baseweb="input"] input { color:#003B5C !important; }
section[data-testid="stSidebar"] button { border-radius:10px; }
section[data-testid="stSidebar"] div[data-testid="stDateInput"] input { color:#003B5C !important; background:#FFFFFF !important; }
section[data-testid="stSidebar"] button p { color: black !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "fictional_sales_data.csv"
    data = pd.read_csv(file_path)
    data["Order_Date"] = pd.to_datetime(data["Order_Date"], errors="coerce")
    for col in ["Units_Sold", "Unit_Price", "Discount_Rate", "Sales", "Cost", "Profit"]:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    return data.dropna(subset=["Order_Date"])

def style_chart(fig, title, height=400, legend=False):
    fig.update_layout(
        title=dict(text=title, x=0.02, y=0.96, xanchor="left", yanchor="top", font=dict(size=18, color=UNHCR_NAVY)),
        height=height,
        margin=dict(l=18, r=18, t=105 if legend else 78, b=25),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#365B6D"),
    )
    if legend:
        fig.update_layout(legend=dict(orientation="h", x=0.02, xanchor="left", y=1.02, yanchor="bottom", title_text="", font=dict(size=12)))
    return fig

df = load_data()

st.markdown("""<div class="dashboard-header"><h1>NovaSphere Sales Intelligence</h1><p>Interactive performance dashboard for a fictional global sales company</p></div>""", unsafe_allow_html=True)

min_date = df["Order_Date"].min().date()
max_date = df["Order_Date"].max().date()

def reset_filters():
    st.session_state["date_range"] = (min_date, max_date)
    st.session_state["region"] = "All regions"
    st.session_state["category"] = "All categories"
    st.session_state["segment"] = "All segments"
    st.session_state["channels"] = sorted(df["Sales_Channel"].dropna().unique().tolist())

with st.sidebar:
    st.header("Dashboard Filters")
    st.button("↻ Clear all filters", use_container_width=True, on_click=reset_filters)
    st.caption("Narrow the dashboard using the controls below.")
    selected_dates = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="date_range")
    selected_region = st.selectbox("Region", ["All regions"] + sorted(df["Region"].dropna().unique().tolist()), key="region")
    selected_category = st.selectbox("Product category", ["All categories"] + sorted(df["Category"].dropna().unique().tolist()), key="category")
    selected_segment = st.selectbox("Customer segment", ["All segments"] + sorted(df["Customer_Segment"].dropna().unique().tolist()), key="segment")
    all_channels = sorted(df["Sales_Channel"].dropna().unique().tolist())
    selected_channels = st.multiselect("Sales channel", all_channels, default=all_channels, key="channels")

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = pd.Timestamp(selected_dates[0]), pd.Timestamp(selected_dates[1])
else:
    start_date, end_date = df["Order_Date"].min(), df["Order_Date"].max()

filtered = df[df["Order_Date"].between(start_date, end_date)].copy()
if selected_region != "All regions": filtered = filtered[filtered["Region"] == selected_region]
if selected_category != "All categories": filtered = filtered[filtered["Category"] == selected_category]
if selected_segment != "All segments": filtered = filtered[filtered["Customer_Segment"] == selected_segment]
filtered = filtered[filtered["Sales_Channel"].isin(selected_channels)]

if filtered.empty:
    st.warning("No sales records match the selected filters. Click 'Clear all filters' to reset the dashboard.")
    st.stop()

total_sales = filtered["Sales"].sum(); total_profit = filtered["Profit"].sum(); orders = filtered["Order_ID"].nunique()
units = int(filtered["Units_Sold"].sum()); margin = total_profit / total_sales if total_sales else 0; avg_order = total_sales / orders if orders else 0
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Total Sales", f"${total_sales:,.0f}"); k2.metric("Total Profit", f"${total_profit:,.0f}"); k3.metric("Profit Margin", f"{margin:.1%}"); k4.metric("Orders", f"{orders:,}"); k5.metric("Average Order", f"${avg_order:,.0f}")

st.markdown('<div class="section-title">Sales trend and product mix</div>', unsafe_allow_html=True)
left,right = st.columns([1.7,1])
monthly = filtered.set_index("Order_Date").resample("MS").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
fig_time = go.Figure()
fig_time.add_trace(go.Scatter(x=monthly["Order_Date"], y=monthly["Sales"], name="Sales", mode="lines+markers", line=dict(color=UNHCR_BLUE,width=3), fill="tozeroy", fillcolor="rgba(0,114,188,0.10)"))
fig_time.add_trace(go.Scatter(x=monthly["Order_Date"], y=monthly["Profit"], name="Profit", mode="lines+markers", line=dict(color=UNHCR_SKY,width=3)))
style_chart(fig_time,"Monthly sales and profit",410,True); fig_time.update_layout(hovermode="x unified"); fig_time.update_yaxes(tickprefix="$",tickformat=",.0f",gridcolor=GRID)
left.plotly_chart(fig_time,use_container_width=True)
category = filtered.groupby("Category",as_index=False)["Sales"].sum().sort_values("Sales",ascending=False)
fig_pie = px.pie(category,names="Category",values="Sales",hole=.58,color_discrete_sequence=COLOR_SEQUENCE)
fig_pie.update_traces(textposition="inside",textinfo="percent+label",hovertemplate="%{label}<br>$%{value:,.0f}<br>%{percent}<extra></extra>")
style_chart(fig_pie,"Sales by category",410,False); fig_pie.update_layout(showlegend=False)
right.plotly_chart(fig_pie,use_container_width=True)

st.markdown('<div class="section-title">Geographic performance</div>', unsafe_allow_html=True)
g1,g2 = st.columns(2)
region_sales = filtered.groupby("Region",as_index=False).agg(Sales=("Sales","sum"),Profit=("Profit","sum")).sort_values("Sales")
fig_region = px.bar(region_sales,x="Sales",y="Region",orientation="h",color="Sales",color_continuous_scale=["#D9F0FA",UNHCR_BLUE],text_auto="$.3s")
style_chart(fig_region,"Sales by region",410); fig_region.update_layout(coloraxis_showscale=False); fig_region.update_xaxes(tickprefix="$",tickformat=",.0f",gridcolor=GRID)
g1.plotly_chart(fig_region,use_container_width=True)
country_sales = filtered.groupby(["Country","Region"],as_index=False).agg(Sales=("Sales","sum"),Profit=("Profit","sum")).nlargest(12,"Sales").sort_values("Sales")
fig_country = px.bar(country_sales,x="Sales",y="Country",orientation="h",color="Region",text_auto="$.3s",color_discrete_sequence=COLOR_SEQUENCE)
style_chart(fig_country,"Top countries by sales",430,True); fig_country.update_xaxes(tickprefix="$",tickformat=",.0f",gridcolor=GRID)
g2.plotly_chart(fig_country,use_container_width=True)

st.markdown('<div class="section-title">Commercial drivers</div>', unsafe_allow_html=True)
c1,c2 = st.columns(2)
product_sales = filtered.groupby("Product",as_index=False)["Sales"].sum().nlargest(10,"Sales").sort_values("Sales")
fig_product = px.bar(product_sales,x="Sales",y="Product",orientation="h",color="Sales",color_continuous_scale=["#D9F0FA",UNHCR_BLUE],text_auto="$.3s")
style_chart(fig_product,"Top 10 products",440); fig_product.update_layout(coloraxis_showscale=False); fig_product.update_xaxes(tickprefix="$",tickformat=",.0f",gridcolor=GRID)
c1.plotly_chart(fig_product,use_container_width=True)
channel = filtered.groupby("Sales_Channel",as_index=False).agg(Sales=("Sales","sum"),Profit=("Profit","sum"))
channel_long = channel.melt(id_vars="Sales_Channel",value_vars=["Sales","Profit"],var_name="Metric",value_name="Amount")
fig_channel = px.bar(channel_long,x="Sales_Channel",y="Amount",color="Metric",barmode="group",color_discrete_map={"Sales":UNHCR_BLUE,"Profit":UNHCR_SKY},text_auto="$.3s")
style_chart(fig_channel,"Sales and profit by channel",440,True); fig_channel.update_yaxes(tickprefix="$",tickformat=",.0f",gridcolor=GRID)
c2.plotly_chart(fig_channel,use_container_width=True)

with st.expander("View and download filtered sales records"):
    display_cols=["Order_ID","Order_Date","Region","Country","Category","Product","Sales_Channel","Customer_Segment","Units_Sold","Sales","Profit"]
    table_data=filtered[display_cols].sort_values("Order_Date",ascending=False).copy(); table_data["Order_Date"]=table_data["Order_Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(table_data,use_container_width=True,hide_index=True,column_config={"Sales":st.column_config.NumberColumn(format="$%.2f"),"Profit":st.column_config.NumberColumn(format="$%.2f")})
    st.download_button("Download filtered CSV",data=filtered.to_csv(index=False).encode("utf-8"),file_name="filtered_sales_data.csv",mime="text/csv")
st.caption(f"Showing {len(filtered):,} of {len(df):,} fictional sales records • {units:,} units sold")
