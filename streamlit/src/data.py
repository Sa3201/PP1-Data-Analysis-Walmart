from __future__ import annotations

from typing import Any

import pandas as pd
import snowflake.connector
import streamlit as st


def _secret(name: str, default: Any = None) -> Any:
    section = st.secrets.get("snowflake", {})
    return section.get(name, default)


@st.cache_resource(show_spinner=False)
def get_connection():
    return snowflake.connector.connect(
        account=_secret("account"),
        user=_secret("user"),
        password=_secret("password"),
        role=_secret("role", "ACCOUNTADMIN"),
        warehouse=_secret("warehouse", "COMPUTE_WH"),
        database=_secret("database", "PP1_WMRT"),
        schema=_secret("schema", "MARTS"),
        client_session_keep_alive=True,
    )


def _query(sql: str) -> pd.DataFrame:
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        return cursor.fetch_pandas_all()
    finally:
        cursor.close()


def load_dashboard_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load sales and feature datasets at their natural grains."""
    database = _secret("database", "PP1_WMRT")
    schema = _secret("schema", "MARTS")
    namespace = f"{database}.{schema}"

    sales_sql = f"""
        select
            fs.department_sales_key,
            fs.store_id,
            fs.dept_id,
            fs.date_id,
            fs.weekly_sales,
            fs.is_holiday,
            ds.store_type,
            ds.store_size,
            dd.week_date,
            dd.day_of_month,
            dd.month_number,
            dd.month_name,
            dd.quarter_number,
            dd.year_number as year
        from {namespace}.fct_department_weekly_sales fs
        join {namespace}.dim_store ds
          on fs.store_id = ds.store_id
        join {namespace}.dim_date dd
          on fs.date_id = dd.date_id
        where fs.is_current = true
    """

    features_sql = f"""
        select
            ff.store_week_key,
            ff.store_id,
            ff.date_id,
            ff.temperature,
            ff.fuel_price,
            ff.markdown_1,
            ff.markdown_2,
            ff.markdown_3,
            ff.markdown_4,
            ff.markdown_5,
            ff.cpi,
            ff.unemployment,
            ds.store_type,
            ds.store_size,
            dd.week_date,
            dd.day_of_month,
            dd.month_number,
            dd.month_name,
            dd.quarter_number,
            dd.year_number as year,
            dd.is_holiday
        from {namespace}.fct_store_weekly_features ff
        join {namespace}.dim_store ds
          on ff.store_id = ds.store_id
        join {namespace}.dim_date dd
          on ff.date_id = dd.date_id
    """

    sales = _query(sales_sql)
    features = _query(features_sql)
    sales["WEEK_DATE"] = pd.to_datetime(sales["WEEK_DATE"])
    features["WEEK_DATE"] = pd.to_datetime(features["WEEK_DATE"])
    return sales, features


def apply_filters(sales: pd.DataFrame, features: pd.DataFrame, filters: dict):
    sales_mask = (
        sales["YEAR"].isin(filters["years"])
        & sales["STORE_TYPE"].isin(filters["store_types"])
    )
    features_mask = (
        features["YEAR"].isin(filters["years"])
        & features["STORE_TYPE"].isin(filters["store_types"])
    )

    # An empty Stores selection means "All stores" and avoids dozens of chips.
    if filters["stores"]:
        sales_mask &= sales["STORE_ID"].isin(filters["stores"])
        features_mask &= features["STORE_ID"].isin(filters["stores"])

    holiday_values = {
        "Holiday": True,
        "Non-holiday": False,
    }
    selected_holiday_values = [holiday_values[item] for item in filters["holidays"]]
    sales_mask &= sales["IS_HOLIDAY"].isin(selected_holiday_values)
    features_mask &= features["IS_HOLIDAY"].isin(selected_holiday_values)

    return sales.loc[sales_mask].copy(), features.loc[features_mask].copy()


def store_week_sales(sales: pd.DataFrame) -> pd.DataFrame:
    """Aggregate department sales before joining to store-week features."""
    return (
        sales.groupby(
            ["STORE_ID", "DATE_ID", "WEEK_DATE", "YEAR"],
            as_index=False,
            observed=True,
        )["WEEKLY_SALES"]
        .sum()
    )
