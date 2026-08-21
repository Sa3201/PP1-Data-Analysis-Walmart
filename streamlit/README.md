# Walmart Retail Analytics - Streamlit

Professional Streamlit dashboard built from the five Snowflake/dbt gold tables.

## Visuals recreated from the requirement PDF

1. Department-wise weekly sales
2. Markdown values by year and store
3. Weekly sales by store type and month
4. Weekly sales by store size
5. Weekly sales by store and holiday status
6. Weekly sales by temperature and year
7. Weekly sales by store type
8. Fuel price by year
9. Weekly sales by year, month, and day
10. Weekly sales by CPI

## Snowflake models used

- `PP1_WMRT.MARTS.DIM_DATE`
- `PP1_WMRT.MARTS.DIM_STORE`
- `PP1_WMRT.MARTS.DIM_DEPARTMENT`
- `PP1_WMRT.MARTS.FCT_DEPARTMENT_WEEKLY_SALES`
- `PP1_WMRT.MARTS.FCT_STORE_WEEKLY_FEATURES`

The dashboard filters both fact tables to `IS_CURRENT = TRUE`.
For CPI and temperature analysis, department sales are aggregated to store-week
grain before joining to the store-week feature fact.

## Local setup

Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r streamlit/requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Enter the Snowflake credentials in `.streamlit/secrets.toml`, then run:

```bash
streamlit run streamlit/app.py
```

Use a dedicated least-privilege Snowflake role in production. It only needs
warehouse usage and `SELECT` access to the five MARTS tables.
