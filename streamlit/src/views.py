from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data import store_week_sales
from src.style import BLUE, CORAL, NAVY, PALETTE, TEAL, YELLOW, money, polish


MONTH_ORDER = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _plot(fig, *, height=430, legend=True):
    with st.container(border=True):
        st.plotly_chart(
            polish(fig, height=height, legend=legend),
            use_container_width=True,
        )


def _currency_axis(fig, values, *, axis="y"):
    """Use business units ($K/$M/$B) instead of Plotly's SI $G notation."""
    numeric = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
    if numeric.empty:
        return
    lower = min(0.0, float(numeric.min()))
    upper = max(0.0, float(numeric.max()))
    if lower == upper:
        upper = lower + 1
    ticks = np.linspace(lower, upper, 6)

    def axis_label(value):
        # Million-scale axis labels use upward-rounded whole values.
        if 1_000_000 <= abs(value) < 1_000_000_000:
            sign = "-" if value < 0 else ""
            rounded = np.ceil(abs(value) / 1_000_000)
            return f"{sign}${rounded:,.0f}M"
        return money(value)

    update = {"tickvals": ticks, "ticktext": [axis_label(value) for value in ticks]}
    if axis == "x":
        fig.update_xaxes(**update)
    else:
        fig.update_yaxes(**update)


def _rounded_millions(value) -> str:
    """Round sales upward to a whole-million bar label."""
    return f"${np.ceil(float(value) / 1_000_000):,.0f}M"


def render_executive_overview(sales: pd.DataFrame, features: pd.DataFrame):
    total_sales = sales["WEEKLY_SALES"].sum()
    stores = sales["STORE_ID"].nunique()
    departments = sales["DEPT_ID"].nunique()
    holiday_sales = sales.loc[sales["IS_HOLIDAY"], "WEEKLY_SALES"].sum()
    holiday_share = holiday_sales / total_sales if total_sales else 0

    cols = st.columns(4)
    cols[0].metric("Total weekly sales", money(total_sales))
    cols[1].metric("Stores", f"{stores:,}")
    cols[2].metric("Departments", f"{departments:,}")
    cols[3].metric("Holiday sales share", f"{holiday_share:.1%}")

    st.markdown("### Sales trend and store-type mix")
    left, right = st.columns([1.8, 1])

    with left:
        trend = sales.groupby("WEEK_DATE", as_index=False)["WEEKLY_SALES"].sum()
        fig = px.line(
            trend,
            x="WEEK_DATE",
            y="WEEKLY_SALES",
            title="Weekly sales trend",
            labels={"WEEK_DATE": "Week", "WEEKLY_SALES": "Weekly sales"},
        )
        fig.update_traces(line=dict(color=BLUE, width=3), fill="tozeroy", fillcolor="rgba(0,113,206,0.10)")
        _currency_axis(fig, trend["WEEKLY_SALES"])
        _plot(fig)

    with right:
        type_sales = sales.groupby("STORE_TYPE", as_index=False)["WEEKLY_SALES"].sum()
        fig = px.pie(
            type_sales,
            names="STORE_TYPE",
            values="WEEKLY_SALES",
            hole=0.58,
            title="Weekly sales by store type",
            color_discrete_sequence=PALETTE,
        )
        fig.update_traces(textposition="inside", textinfo="label+percent")
        _plot(fig)

    top_stores = (
        sales.groupby("STORE_ID", as_index=False)["WEEKLY_SALES"]
        .sum()
        .nlargest(10, "WEEKLY_SALES")
        .sort_values("WEEKLY_SALES", ascending=False)
        .drop_duplicates(subset=["STORE_ID"])
        .reset_index(drop=True)
    )
    top_stores["STORE"] = "Store " + top_stores["STORE_ID"].astype(int).astype(str)
    top_stores["SALES_LABEL"] = top_stores["WEEKLY_SALES"].map(_rounded_millions)
    fig = px.bar(
        top_stores,
        x="STORE",
        y="WEEKLY_SALES",
        text="SALES_LABEL",
        title="Top 10 stores by weekly sales",
        labels={"STORE": "Store", "WEEKLY_SALES": "Weekly sales"},
        category_orders={"STORE": top_stores["STORE"].tolist()},
        color_discrete_sequence=[BLUE],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(type="category")
    _currency_axis(fig, top_stores["WEEKLY_SALES"])
    _plot(fig, height=450, legend=False)


def render_sales_performance(sales: pd.DataFrame):
    st.markdown("### Weekly sales by year, month and day")
    year_col, month_col = st.columns([1, 2])
    with year_col:
        yearly = sales.groupby("YEAR", as_index=False)["WEEKLY_SALES"].sum()
        yearly["YEAR"] = yearly["YEAR"].astype(int).astype(str)
        yearly["SALES_LABEL"] = yearly["WEEKLY_SALES"].map(_rounded_millions)
        fig = px.bar(
            yearly,
            x="YEAR",
            y="WEEKLY_SALES",
            title="Sales by year",
            text="SALES_LABEL",
            labels={"YEAR": "Year", "WEEKLY_SALES": "Weekly sales"},
            color_discrete_sequence=[BLUE],
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(type="category")
        _currency_axis(fig, yearly["WEEKLY_SALES"])
        _plot(fig, height=380, legend=False)

    with month_col:
        monthly = sales.groupby("MONTH_NUMBER", as_index=False)["WEEKLY_SALES"].sum()
        monthly["MONTH"] = monthly["MONTH_NUMBER"].map(lambda m: MONTH_ORDER[int(m) - 1])
        monthly["SALES_LABEL"] = monthly["WEEKLY_SALES"].map(_rounded_millions)
        fig = px.bar(
            monthly,
            x="MONTH",
            y="WEEKLY_SALES",
            title="Sales by month",
            text="SALES_LABEL",
            category_orders={"MONTH": MONTH_ORDER},
            color_discrete_sequence=[BLUE],
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        _currency_axis(fig, monthly["WEEKLY_SALES"])
        _plot(fig, height=380, legend=False)

    daily = sales.groupby("DAY_OF_MONTH", as_index=False)["WEEKLY_SALES"].sum()
    fig = px.bar(
        daily,
        x="DAY_OF_MONTH",
        y="WEEKLY_SALES",
        title="Sales by day of month",
        labels={"DAY_OF_MONTH": "Day", "WEEKLY_SALES": "Weekly sales"},
        color_discrete_sequence=[TEAL],
    )
    _currency_axis(fig, daily["WEEKLY_SALES"])
    _plot(fig, height=390, legend=False)

    st.markdown("### Weekly sales by store type and month")
    type_month = sales.groupby(["MONTH_NUMBER", "STORE_TYPE"], as_index=False)["WEEKLY_SALES"].sum()
    type_month["MONTH"] = type_month["MONTH_NUMBER"].map(lambda m: MONTH_ORDER[int(m) - 1])
    fig = px.line(
        type_month,
        x="MONTH",
        y="WEEKLY_SALES",
        color="STORE_TYPE",
        markers=True,
        title="Monthly sales trend by store type",
        category_orders={"MONTH": MONTH_ORDER},
        labels={"MONTH": "Month", "WEEKLY_SALES": "Weekly sales", "STORE_TYPE": "Store type"},
        color_discrete_sequence=PALETTE,
    )
    fig.update_traces(line=dict(width=3))
    _currency_axis(fig, type_month["WEEKLY_SALES"])
    _plot(fig)

    st.markdown("### Weekly sales by store and holiday")
    holiday = sales.groupby(["STORE_ID", "IS_HOLIDAY"], as_index=False)["WEEKLY_SALES"].sum()
    holiday["HOLIDAY_STATUS"] = np.where(holiday["IS_HOLIDAY"], "Holiday", "Non-holiday")
    fig = px.bar(
        holiday,
        x="STORE_ID",
        y="WEEKLY_SALES",
        color="HOLIDAY_STATUS",
        barmode="group",
        title="Store sales: holiday vs non-holiday weeks",
        labels={"STORE_ID": "Store", "WEEKLY_SALES": "Weekly sales", "HOLIDAY_STATUS": "Week type"},
        color_discrete_map={"Holiday": YELLOW, "Non-holiday": BLUE},
    )
    _currency_axis(fig, holiday["WEEKLY_SALES"])
    _plot(fig, height=480)


def render_store_department(sales: pd.DataFrame):
    st.markdown("### Department-wise weekly sales")
    dept = sales.groupby("DEPT_ID", as_index=False)["WEEKLY_SALES"].sum()
    best_department = dept.nlargest(1, "WEEKLY_SALES").iloc[0]
    worst_department = dept.nsmallest(1, "WEEKLY_SALES").iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total weekly sales", money(dept["WEEKLY_SALES"].sum()))
    c2.metric(
        f"Best Selling Department · Dept {int(best_department['DEPT_ID'])}",
        money(best_department["WEEKLY_SALES"]),
    )
    c3.metric(
        f"Worst Selling Department · Dept {int(worst_department['DEPT_ID'])}",
        money(worst_department["WEEKLY_SALES"]),
    )

    top_departments = dept.nlargest(10, "WEEKLY_SALES").sort_values("WEEKLY_SALES", ascending=False).copy()
    top_departments["DEPARTMENT"] = "Department " + top_departments["DEPT_ID"].astype(str)
    top_departments["SALES_LABEL"] = top_departments["WEEKLY_SALES"].map(_rounded_millions)
    fig = px.bar(
        top_departments,
        x="DEPARTMENT",
        y="WEEKLY_SALES",
        text="SALES_LABEL",
        title="Top 10 departments by weekly sales",
        labels={"DEPARTMENT": "Department", "WEEKLY_SALES": "Weekly sales"},
        category_orders={"DEPARTMENT": top_departments["DEPARTMENT"].tolist()},
        color_discrete_sequence=[YELLOW],
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(type="category", tickangle=-45)
    _currency_axis(fig, top_departments["WEEKLY_SALES"])
    _plot(fig, height=450, legend=False)

    fig = px.bar(
        dept,
        x="DEPT_ID",
        y="WEEKLY_SALES",
        title="Weekly sales by department",
        labels={"DEPT_ID": "Department", "WEEKLY_SALES": "Weekly sales"},
        color="WEEKLY_SALES",
        color_continuous_scale=[[0, "#DCEEFF"], [1, BLUE]],
    )
    fig.update_layout(coloraxis_showscale=False)
    _currency_axis(fig, dept["WEEKLY_SALES"])
    _plot(fig, height=470, legend=False)

    st.markdown("### Weekly sales by store size")
    size_sales = sales.groupby(["STORE_ID", "STORE_SIZE", "STORE_TYPE"], as_index=False)["WEEKLY_SALES"].sum()
    fig = px.scatter(
        size_sales,
        x="STORE_SIZE",
        y="WEEKLY_SALES",
        color="STORE_TYPE",
        size="WEEKLY_SALES",
        hover_name="STORE_ID",
        title="Relationship between store size and weekly sales",
        labels={"STORE_SIZE": "Store size", "WEEKLY_SALES": "Weekly sales", "STORE_TYPE": "Store type"},
        color_discrete_sequence=PALETTE,
        trendline="ols" if len(size_sales) >= 2 else None,
    )
    _currency_axis(fig, size_sales["WEEKLY_SALES"])
    _plot(fig, height=480)

    st.markdown("### Weekly sales by store type")
    type_sales = sales.groupby("STORE_TYPE", as_index=False)["WEEKLY_SALES"].sum()
    store_type = sales.groupby(["STORE_ID", "STORE_TYPE"], as_index=False)["WEEKLY_SALES"].sum()
    left, right = st.columns([1, 2])
    with left:
        fig = px.pie(
            type_sales,
            names="STORE_TYPE",
            values="WEEKLY_SALES",
            hole=0.52,
            title="Sales mix by store type",
            color_discrete_sequence=PALETTE,
        )
        fig.update_traces(textinfo="label+percent")
        _plot(fig)
    with right:
        fig = px.bar(
            store_type,
            x="WEEKLY_SALES",
            y=store_type["STORE_ID"].astype(str),
            color="STORE_TYPE",
            orientation="h",
            title="Store sales grouped by type",
            labels={"x": "Weekly sales", "y": "Store", "STORE_TYPE": "Store type"},
            color_discrete_sequence=PALETTE,
        )
        _currency_axis(fig, store_type["WEEKLY_SALES"], axis="x")
        _plot(fig, height=max(430, len(store_type) * 22))


def render_market_factors(sales: pd.DataFrame, features: pd.DataFrame):
    st.markdown("### Markdown sales by year and store")
    markdown_cols = [f"MARKDOWN_{i}" for i in range(1, 6)]
    markdown = features.groupby("YEAR", as_index=False)[markdown_cols].sum(min_count=1)
    markdown["YEAR"] = markdown["YEAR"].astype(int).astype(str)
    markdown_long = markdown.melt(
        id_vars="YEAR",
        value_vars=markdown_cols,
        var_name="MARKDOWN_TYPE",
        value_name="MARKDOWN_VALUE",
    )
    markdown_long["MARKDOWN_TYPE"] = markdown_long["MARKDOWN_TYPE"].str.replace("_", " ").str.title()
    fig = px.bar(
        markdown_long,
        x="YEAR",
        y="MARKDOWN_VALUE",
        color="MARKDOWN_TYPE",
        barmode="group",
        title="Markdown totals by year",
        labels={"YEAR": "Year", "MARKDOWN_VALUE": "Markdown amount", "MARKDOWN_TYPE": "Markdown"},
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(type="category")
    _currency_axis(fig, markdown_long["MARKDOWN_VALUE"])
    _plot(fig)

    with st.expander("View markdown values by store"):
        store_markdowns = features.groupby(["YEAR", "STORE_ID"], as_index=False)[markdown_cols].sum(min_count=1)
        st.dataframe(store_markdowns, hide_index=True, width="stretch")

    st.markdown("### Fuel price by year")
    fuel = features.groupby("YEAR", as_index=False)["FUEL_PRICE"].mean()
    fuel["YEAR"] = fuel["YEAR"].astype(int).astype(str)
    year_order = sorted(fuel["YEAR"].unique().tolist())
    fig = px.bar(
        fuel,
        x="YEAR",
        y="FUEL_PRICE",
        title="Average fuel price by year",
        text_auto="$.2f",
        category_orders={"YEAR": year_order},
        color_discrete_sequence=[BLUE],
    )
    fig.update_xaxes(type="category", title="Year")
    fig.update_yaxes(tickprefix="$", tickformat=".2f")
    _plot(fig, height=410, legend=False)

    store_sales = store_week_sales(sales)
    analysis = store_sales.merge(
        features[
            ["STORE_ID", "DATE_ID", "TEMPERATURE", "CPI", "UNEMPLOYMENT", "YEAR"]
        ],
        on=["STORE_ID", "DATE_ID"],
        how="inner",
        suffixes=("_SALES", "_FEATURE"),
    )
    analysis["YEAR_LABEL"] = analysis["YEAR_FEATURE"].astype(int).astype(str)

    st.markdown("### Weekly sales by temperature and year")
    fig = px.scatter(
        analysis,
        x="TEMPERATURE",
        y="WEEKLY_SALES",
        color="YEAR_LABEL",
        opacity=0.62,
        trendline="lowess" if len(analysis) >= 10 else None,
        title="Store-week sales compared with temperature",
        labels={"TEMPERATURE": "Temperature (°F)", "WEEKLY_SALES": "Weekly sales", "YEAR_LABEL": "Year"},
        color_discrete_sequence=PALETTE,
    )
    _currency_axis(fig, analysis["WEEKLY_SALES"])
    _plot(fig, height=480)

    st.markdown("### Weekly sales by CPI")
    fig = px.scatter(
        analysis,
        x="CPI",
        y="WEEKLY_SALES",
        color="YEAR_LABEL",
        opacity=0.62,
        trendline="lowess" if len(analysis) >= 10 else None,
        title="Store-week sales compared with CPI",
        labels={"CPI": "Consumer Price Index", "WEEKLY_SALES": "Weekly sales", "YEAR_LABEL": "Year"},
        color_discrete_sequence=PALETTE,
    )
    _currency_axis(fig, analysis["WEEKLY_SALES"])
    _plot(fig, height=480)
