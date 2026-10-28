"""Small Streamlit dashboard for the salary and layoffs project."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


ROOT = Path(__file__).resolve().parent
SALARY_FILE = ROOT / "india_salary_benchmarks_2026_sample.csv"
LAYOFFS_FILE = ROOT / "layoffs-2026.csv"

st.set_page_config(page_title="Tech Salaries & Layoffs", page_icon="📊", layout="wide")


@st.cache_data
def load_data():
    salaries = pd.read_csv(SALARY_FILE)
    layoffs = pd.read_csv(LAYOFFS_FILE, comment="#")
    salaries["salary_mid_inr"] = pd.to_numeric(salaries["salary_mid_inr"], errors="coerce")
    layoffs["People Cut"] = pd.to_numeric(layoffs["People Cut"], errors="coerce")
    return salaries, layoffs


st.title("Tech Salaries & Layoffs")
st.caption("Explore the India salary posting sample and the 2026 reported layoffs snapshot.")

try:
    salary_data, layoffs_data = load_data()
except FileNotFoundError as error:
    st.error(f"Couldn't find a project CSV: {error.filename}. Keep both data files beside app.py.")
    st.stop()

salary_data["posted_month_dt"] = pd.to_datetime(salary_data["posted_month"], format="%Y-%m", errors="coerce")
salary_data["month_index"] = (
    salary_data["posted_month_dt"].dt.year * 12 + salary_data["posted_month_dt"].dt.month
)
model_data = salary_data.dropna(subset=["month_index", "salary_mid_inr"])
month_model = LinearRegression().fit(model_data[["month_index"]], model_data["salary_mid_inr"])
trend_r2 = r2_score(model_data["salary_mid_inr"], month_model.predict(model_data[["month_index"]]))

with st.sidebar:
    st.header("Salary filters")
    roles = sorted(salary_data["role_family"].dropna().unique())
    selected_roles = st.multiselect("Role family", roles, default=roles)
    seniorities = sorted(salary_data["seniority"].dropna().unique())
    selected_seniorities = st.multiselect("Seniority", seniorities, default=seniorities)
    cities = sorted(salary_data["city"].dropna().unique())
    selected_cities = st.multiselect("City", cities, default=[] , help="Leave empty to include every city.")

filtered = salary_data[
    salary_data["role_family"].isin(selected_roles)
    & salary_data["seniority"].isin(selected_seniorities)
]
if selected_cities:
    filtered = filtered[filtered["city"].isin(selected_cities)]
filtered = filtered.dropna(subset=["salary_mid_inr"])

tab_salary, tab_layoffs, tab_about = st.tabs(["Salary explorer", "Layoffs snapshot", "About the data"])

with tab_salary:
    st.subheader("Salary estimate by posting month")
    available_months = sorted(salary_data["posted_month"].dropna().unique())
    selected_month = st.selectbox("Select a posting month", available_months, index=len(available_months) - 1)
    selected_month_index = pd.Period(selected_month, freq="M").year * 12 + pd.Period(selected_month, freq="M").month
    estimated_salary = float(month_model.predict(pd.DataFrame({"month_index": [selected_month_index]}))[0])
    if estimated_salary > 0:
        st.metric("Estimated annual salary midpoint", f"₹{estimated_salary:,.0f}")
    else:
        st.warning(f"The model estimates ₹{estimated_salary:,.0f}, which is not a realistic salary estimate.")
    st.caption(
        f"Simple month only linear regression based on all {len(model_data):,} postings. "
        f"Its R² is {trend_r2:.3f}, so month explains little of the salary variation; "
        "treat this as a classroom demonstration, not an individual salary forecast."
    )

    if filtered.empty:
        st.info("No postings match these filters. Adjust the selections in the sidebar.")
    else:
        median = filtered["salary_mid_inr"].median()
        mean = filtered["salary_mid_inr"].mean()
        c1, c2, c3 = st.columns(3)
        c1.metric("Postings", f"{len(filtered):,}")
        c2.metric("Median salary", f"₹{median:,.0f}")
        c3.metric("Mean salary", f"₹{mean:,.0f}")

        left, right = st.columns(2)
        with left:
            st.subheader("Salary distribution")
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.hist(filtered["salary_mid_inr"] / 100_000, bins=40, color="#3977b8", edgecolor="white")
            ax.set_xlabel("Annual salary midpoint (₹ lakh)")
            ax.set_ylabel("Postings")
            ax.spines[["top", "right"]].set_visible(False)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        with right:
            st.subheader("Median salary by role")
            by_role = (filtered.groupby("role_family")["salary_mid_inr"].median()
                       .sort_values().tail(12) / 100_000)
            fig, ax = plt.subplots(figsize=(7, 4))
            by_role.plot.barh(ax=ax, color="#53a58b")
            ax.set_xlabel("Median annual salary (₹ lakh)")
            ax.set_ylabel("")
            ax.spines[["top", "right"]].set_visible(False)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        monthly = filtered.assign(month=pd.to_datetime(filtered["posted_month"], errors="coerce"))
        monthly = monthly.dropna(subset=["month"]).groupby("month")["salary_mid_inr"].median() / 100_000
        st.subheader("Monthly median salary")
        st.line_chart(monthly.rename("Median salary (₹ lakh)"), use_container_width=True)

with tab_layoffs:
    total_cut = layoffs_data["People Cut"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Reported events", f"{len(layoffs_data):,}")
    c2.metric("Reported people cut", f"{total_cut:,.0f}")
    c3.metric("Industries", f"{layoffs_data['Industry'].nunique():,}")
    left, right = st.columns(2)
    with left:
        st.subheader("Events by category")
        st.bar_chart(layoffs_data["Category"].value_counts(), use_container_width=True)
    with right:
        st.subheader("Reported people cut by industry")
        industry = layoffs_data.groupby("Industry")["People Cut"].sum().sort_values().tail(12)
        st.bar_chart(industry, use_container_width=True)
    with st.expander("View reported events"):
        st.dataframe(layoffs_data, use_container_width=True, hide_index=True)

with tab_about:
    st.markdown("""
    **Salary data:** a sample of 12,958 India salary postings from January 2024 to June 2026.
    Values are advertised annual salary midpoints in INR. The sample is observational and is
    not a guaranteed market-wide estimate.

    **Layoffs data:** a snapshot of reported 2026 events. It is incomplete, and some source
    dates do not include a year or use non-standard formats. Counts describe reported events
    only; they are not a complete time series.

    Sources and project methodology are documented in `README.md` and the accompanying notebook.
    """)
