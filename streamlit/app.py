from __future__ import annotations

import streamlit as st

from src.data import apply_filters, load_dashboard_data
from src.views import (
    render_executive_overview,
    render_market_factors,
    render_sales_performance,
    render_store_department,
)


st.set_page_config(
    page_title="Walmart Retail Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
      .stApp { background: #f6f8fb; }
      [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e5eaf0; }
      [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5eaf0;
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 2px 10px rgba(20, 52, 83, 0.05);
      }
      [data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border: 1px solid #dfe7ef !important;
        border-top: 4px solid #0071ce !important;
        border-radius: 14px !important;
        box-shadow: 0 5px 18px rgba(18, 52, 77, 0.08);
        padding: 0.35rem 0.55rem 0.25rem 0.55rem;
      }
      [data-testid="stRadio"] > div[role="radiogroup"] {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.65rem;
        width: 100%;
      }
      [data-testid="stRadio"] > div[role="radiogroup"] > label {
        background: #ffffff;
        border: 1px solid #dce5ee;
        border-radius: 10px;
        justify-content: center;
        min-height: 46px;
        padding: 0.55rem 0.7rem;
        box-shadow: 0 2px 8px rgba(18, 52, 77, 0.05);
      }
      [data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
        background: #eaf4ff;
        border-color: #0071ce;
        color: #00589f;
        font-weight: 700;
      }
      .dashboard-hero {
        background: linear-gradient(120deg, #062f4f 0%, #0071ce 62%, #35a7e8 100%);
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(0, 71, 206, 0.18);
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 1rem;
        min-height: 140px;
        overflow: hidden;
        padding: 1.5rem 2rem 1.35rem 2rem;
        position: relative;
      }
      .dashboard-hero::after {
        background: #ffc220;
        border-radius: 999px;
        content: "";
        height: 9px;
        position: absolute;
        right: 2rem;
        top: 1.8rem;
        width: 72px;
      }
      .dashboard-hero .dashboard-title {
        color: #ffffff;
        font-family: "Avenir Next", "Segoe UI", Arial, sans-serif;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        letter-spacing: -0.03em;
        line-height: 1.02 !important;
        margin: 0 !important;
      }
      .dashboard-hero .dashboard-subtitle {
        color: #e7f4ff;
        font-family: "Avenir Next", "Segoe UI", Arial, sans-serif;
        font-size: 1.25rem !important;
        font-weight: 500;
        margin: 0.7rem 0 0 0 !important;
      }
      @media (max-width: 850px) {
        .dashboard-hero { min-height: 120px; padding: 1.35rem; }
        .dashboard-hero .dashboard-title { font-size: 2.15rem !important; }
        .dashboard-hero .dashboard-subtitle { font-size: 1rem !important; }
      }
      h1, h2, h3 { color: #12344d; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=900, show_spinner="Loading Walmart gold tables from Snowflake...")
def get_data():
    return load_dashboard_data()


def sidebar_filters(sales, features):
    st.sidebar.markdown("## Walmart Retail Analytics")
    st.sidebar.caption("AWS S3 | Snowflake | dbt | Streamlit | Plotly")
    st.sidebar.markdown("### Filters")

    years = sorted(sales["YEAR"].dropna().astype(int).unique().tolist())
    selected_years = st.sidebar.multiselect("Year", years, default=years)

    store_types = sorted(sales["STORE_TYPE"].dropna().astype(str).unique().tolist())
    selected_types = st.sidebar.multiselect("Store type", store_types, default=store_types)

    holiday_choices = ["Holiday", "Non-holiday"]
    selected_holidays = st.sidebar.multiselect(
        "Holiday week",
        holiday_choices,
        default=holiday_choices,
    )

    stores = sorted(sales["STORE_ID"].dropna().astype(int).unique().tolist())
    selected_stores = st.sidebar.multiselect(
        "Stores",
        stores,
        default=[],
        placeholder="All stores",
        help="Leave blank to include every store, or select one or more stores to filter.",
    )

    if st.sidebar.button("Refresh Snowflake data", width="stretch"):
        st.cache_data.clear()
        st.rerun()

    filters = {
        "years": selected_years,
        "store_types": selected_types,
        "stores": selected_stores,
        "holidays": selected_holidays,
    }
    return apply_filters(sales, features, filters)


try:
    sales_df, features_df = get_data()
except Exception as exc:
    st.error("The dashboard could not connect to Snowflake.")
    st.info(
        "Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, "
        "add your Snowflake credentials, and confirm that the five MARTS tables exist."
    )
    with st.expander("Connection details"):
        st.exception(exc)
    st.stop()

filtered_sales, filtered_features = sidebar_filters(sales_df, features_df)

st.markdown(
    """
    <div class="dashboard-hero">
      <p class="dashboard-title">Walmart Retail Analytics</p>
      <p class="dashboard-subtitle">Interactive sales, store and economic performance dashboard</p>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.radio(
    "Dashboard page",
    [
        "Executive Overview",
        "Sales Performance",
        "Store & Department",
        "Market Factors",
    ],
    horizontal=True,
    label_visibility="collapsed",
)
st.markdown("<div style='height: 0.65rem'></div>", unsafe_allow_html=True)

if filtered_sales.empty:
    st.warning("No sales records match the current filters. Adjust the sidebar selections.")
    st.stop()

if page == "Executive Overview":
    render_executive_overview(filtered_sales, filtered_features)
elif page == "Sales Performance":
    render_sales_performance(filtered_sales)
elif page == "Store & Department":
    render_store_department(filtered_sales)
else:
    render_market_factors(filtered_sales, filtered_features)
