import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# ------------------------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Executive Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# ------------------------------------------------------------------------------
# DATA LOADING & PREPROCESSING
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Load standard Superstore dataset
    # Ensure 'superstore.csv' is in the same directory
    df = pd.read_csv("superstore.csv", encoding="ISO-8859-1")
    
    # Standardize column names (optional, depends on source file)
    # This maps common variations to a standard format
    df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
    
    # Date conversion
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'])
        
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File 'superstore.csv' not found. Please download the dataset and place it in the project folder.")
    st.stop()

# ------------------------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------------------------
st.sidebar.header("Filter Data")

# 1. Region Filter
region = st.sidebar.multiselect(
    "Select Region:",
    options=df["region"].unique(),
    default=df["region"].unique()
)

# 2. State Filter (Dynamic based on Region)
# If specific regions are selected, only show states from those regions
if not region:
    df_region = df.copy()
else:
    df_region = df[df["region"].isin(region)]

state = st.sidebar.multiselect(
    "Select State:",
    options=df_region["state"].unique(),
    default=df_region["state"].unique()
)

# 3. Category Filter
category = st.sidebar.multiselect(
    "Select Category:",
    options=df_region["category"].unique(),
    default=df_region["category"].unique()
)

# Apply filters to the main dataframe
df_selection = df.query(
    "region == @region & state == @state & category == @category"
)

# ------------------------------------------------------------------------------
# MAIN DASHBOARD UI
# ------------------------------------------------------------------------------

# Title
st.title("📊 Executive Sales Performance Dashboard")
st.markdown("##")

# KPI SECTION (Top Row)
total_sales = int(df_selection["sales"].sum())
total_profit = int(df_selection["profit"].sum())
avg_rating = round(df_selection["profit"].mean(), 2) 

left_column, middle_column, right_column = st.columns(3)

with left_column:
    st.subheader("Total Sales")
    st.subheader(f"US $ {total_sales:,}")

with middle_column:
    st.subheader("Total Profit")
    st.subheader(f"US $ {total_profit:,}")

with right_column:
    st.subheader("Average Profit per Sale")
    st.subheader(f"US $ {avg_rating}")

st.markdown("""---""")

# ------------------------------------------------------------------------------
# CHARTS SECTION
# ------------------------------------------------------------------------------

# ROW 1: SALES BY PRODUCT LINE & TREND
col1, col2 = st.columns(2)  # <--- INI BARIS PENTING YANG HILANG TADI

with col1:
    st.subheader("Sales by Product Category")
    
    # FIX: Kita jumlahkan dulu sales-nya berdasarkan kategori
    sales_by_category = df_selection.groupby(by=["category"])[["sales"]].sum().sort_values(by="sales")

    fig_product_sales = px.bar(
        sales_by_category,
        x="sales",
        y=sales_by_category.index,
        orientation="h",
        template="plotly_white",
        color_discrete_sequence=["#0083B8"] * len(sales_by_category),
    )
    fig_product_sales.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)))
    st.plotly_chart(fig_product_sales, use_container_width=True)

with col2:
    st.subheader("Monthly Sales Trend")
    # Group by month
    df_selection["month_year"] = df_selection["order_date"].dt.to_period("M")
    line_chart_data = df_selection.groupby(df_selection["month_year"].dt.strftime("%Y-%m"))["sales"].sum().reset_index()
    
    fig_sales_trend = px.line(
        line_chart_data,
        x="month_year",
        y="sales",
        template="plotly_white",
        markers=True
    )
    fig_sales_trend.update_layout(plot_bgcolor="rgba(0,0,0,0)", yaxis=(dict(showgrid=False)))
    st.plotly_chart(fig_sales_trend, use_container_width=True)

# ROW 2: DETAILED DATA VIEW
st.markdown("""---""")
st.subheader("Detailed Data View")

with st.expander("Click to view Raw Data"):
    st.dataframe(df_selection)
    
    # DOWNLOAD BUTTON
    csv = df_selection.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_sales_data.csv',
        mime='text/csv',
    )