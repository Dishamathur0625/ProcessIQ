import streamlit as st
import pandas as pd

from modules.statistics.statistics import Statistics
from modules.statistics.quality import DataQuality

st.set_page_config(
    page_title="ProcessIQ Dashboard",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 ProcessIQ")
st.caption("Industrial Data Analytics Platform")

st.divider()

# -------------------------------------------------------
# No Dataset
# -------------------------------------------------------

if "dataset" not in st.session_state:

    st.info("Upload a dataset to begin analysis.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.success("① Upload Dataset")

    with c2:
        st.info("② Analyze Data")

    with c3:
        st.warning("③ Generate Reports")

    st.stop()

# -------------------------------------------------------
# Dataset
# -------------------------------------------------------

df = st.session_state["dataset"]

summary = Statistics.generate(df)
quality = DataQuality.calculate(df)

# -------------------------------------------------------
# KPI Cards
# -------------------------------------------------------

st.subheader("Dataset Overview")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Rows",
    summary["rows"]
)

c2.metric(
    "Columns",
    summary["columns"]
)

c3.metric(
    "Missing",
    summary["missing"]
)

c4.metric(
    "Duplicates",
    summary["duplicate_rows"]
)

c5.metric(
    "Quality",
    f"{quality['score']}%"
)

st.divider()

# -------------------------------------------------------
# Dataset Info
# -------------------------------------------------------

left, right = st.columns([2, 1])

with left:

    st.subheader("Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

with right:

    st.subheader("Data Quality")

    st.metric(
        "Overall Rating",
        quality["rating"]
    )

    st.metric(
        "Completeness",
        f"{quality['completeness']}%"
    )

    st.metric(
        "Uniqueness",
        f"{quality['uniqueness']}%"
    )

st.divider()

# -------------------------------------------------------
# Workflow
# -------------------------------------------------------

st.subheader("Workflow Progress")

progress = 90

st.progress(progress)

st.success(f"Project Progress : {progress}%")

st.write("""
✅ Upload Completed

✅ Validation Completed

✅ Alignment Completed

✅ Aggregation Completed

✅ Statistics Completed

🟡 Correlation (Pending)

🟡 Prediction (Pending)

🟡 Final Report (Pending)
""")