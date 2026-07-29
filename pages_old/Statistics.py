import streamlit as st

from modules.statistics.statistics import Statistics
from modules.statistics.quality import DataQuality
from modules.statistics.charts import Charts
from modules.reports.export_excel import ExcelExporter

st.set_page_config(
    page_title="Statistics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ProcessIQ Analytics Dashboard")

if "dataset" not in st.session_state:
    st.warning("Please upload a dataset first.")
    st.stop()

df = st.session_state["dataset"]

# ============================================================
# Generate Reports
# ============================================================

summary = Statistics.generate(df)
quality = DataQuality.calculate(df)
variable_summary = Statistics.variable_summary(df)
missing = Statistics.missing_values(df)

# ============================================================
# KPI Cards
# ============================================================

st.subheader("Overview")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Rows", summary["rows"])

c2.metric("Columns", summary["columns"])

c3.metric(
    "Missing %",
    f"{summary['missing_percentage']}%"
)

c4.metric(
    "Duplicate Rows",
    summary["duplicate_rows"]
)

c5.metric(
    "Quality Score",
    f"{quality['score']}%"
)

st.success(
    f"""
Overall Rating : **{quality['rating']}**

Completeness : **{quality['completeness']}%**

Uniqueness : **{quality['uniqueness']}%**
"""
)

st.divider()

# ============================================================
# Dataset Preview
# ============================================================

left, right = st.columns([2, 1])

with left:

    st.subheader("Dataset Preview")

    preview = st.slider(
        "Rows",
        5,
        100,
        10
    )

    st.dataframe(
        df.head(preview),
        use_container_width=True
    )

with right:

    st.subheader("Missing Values")

    st.dataframe(
        missing,
        use_container_width=True
    )

st.divider()

# ============================================================
# Variable Summary
# ============================================================

st.subheader("Variable Summary")

st.dataframe(
    variable_summary,
    use_container_width=True
)

st.divider()

# ============================================================
# Charts
# ============================================================

left, right = st.columns(2)

numeric_columns = list(
    df.select_dtypes(include="number").columns
)

with left:

    st.subheader("Distribution")

    if numeric_columns:

        column = st.selectbox(
            "Variable",
            numeric_columns
        )

        fig = Charts.histogram(
            df,
            column
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with right:

    st.subheader("Box Plot")

    fig = Charts.boxplot(df)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# ============================================================
# Missing Value Graph
# ============================================================

st.subheader("Missing Value Analysis")

fig = Charts.missing_chart(df)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# ============================================================
# Time Trend
# ============================================================

timestamp_columns = [
    c for c in df.columns
    if c.lower() in [
        "datetime",
        "timestamp",
        "date",
        "time",
        "date_time"
    ]
]

if timestamp_columns and numeric_columns:

    st.subheader("Time Series")

    y = st.selectbox(
        "Select Variable",
        numeric_columns,
        key="trend"
    )

    fig = Charts.line_chart(
        df,
        timestamp_columns[0],
        y
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.divider()

# ============================================================
# Export
# ============================================================

st.subheader("Export")

excel = ExcelExporter.export(df)

st.download_button(
    "📥 Download Processed Dataset",
    excel,
    "Processed_Dataset.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)