import streamlit as st

from modules.ingestion.loader import FileLoader
from modules.ingestion.validation import DataValidator
from modules.preprocessing.alignment import DataAlignment
from modules.preprocessing.aggregation import TimeAggregation


st.set_page_config(
    page_title="Upload Dataset",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Upload Dataset")

st.write(
    "Upload industrial datasets (.csv, .xls, .xlsx) for preprocessing and analysis."
)

uploaded_file = st.file_uploader(
    "Choose Dataset",
    type=["csv", "xls", "xlsx"]
)

if uploaded_file:

    # -------------------------
    # Load Dataset
    # -------------------------
    df = FileLoader.load(uploaded_file)

    # -------------------------
    # Validate Dataset
    # -------------------------
    validation_report = DataValidator.validate(df)

    if not validation_report["valid"]:
        st.error(validation_report["message"])
        st.stop()

    # -------------------------
    # Alignment
    # -------------------------
    df, alignment_report = DataAlignment.clean(df)

    # -------------------------
    # Save Clean Dataset
    # -------------------------
    st.session_state["dataset"] = df

    st.success("Dataset uploaded and aligned successfully.")

    # ==========================================================
    # Dataset Information
    # ==========================================================

    st.subheader("📊 Dataset Information")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Rows", validation_report["rows"])
    c2.metric("Columns", validation_report["columns"])
    c3.metric("Missing Values", validation_report["missing_values"])
    c4.metric("Duplicate Rows", validation_report["duplicate_rows"])

    st.divider()

    # ==========================================================
    # Alignment Summary
    # ==========================================================

    st.subheader("🧹 Alignment Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Original Rows", alignment_report["original_rows"])
    c2.metric("Processed Rows", alignment_report["processed_rows"])
    c3.metric("Duplicates Removed", alignment_report["duplicates_removed"])
    c4.metric(
        "Timestamp Column",
        alignment_report["timestamp_column"]
        if alignment_report["timestamp_column"]
        else "Not Found"
    )

    st.divider()

    # ==========================================================
    # Dataset Preview
    # ==========================================================

    st.subheader("📄 Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

    st.divider()

    # ==========================================================
    # Aggregation
    # ==========================================================

    st.subheader("⏱ Time Aggregation")

    interval = st.selectbox(
        "Sampling Interval",
        [
            "1min",
            "5min",
            "15min",
            "30min",
            "1H"
        ]
    )

    method = st.selectbox(
        "Aggregation Method",
        [
            "Mean",
            "Median",
            "Max",
            "Min",
            "Sum"
        ]
    )

    if st.button("Aggregate Dataset"):

        aggregated_df, aggregation_report = TimeAggregation.aggregate(
            df,
            interval,
            method
        )

        st.session_state["dataset"] = aggregated_df

        st.success("Aggregation completed successfully.")

        st.subheader("Aggregation Summary")

        c1, c2, c3 = st.columns(3)

        c1.metric("Interval", aggregation_report["interval"])
        c2.metric("Method", aggregation_report["method"])
        c3.metric(
            "Rows",
            f'{aggregation_report["input_rows"]} → {aggregation_report["output_rows"]}'
        )

        st.dataframe(
            aggregated_df.head(10),
            use_container_width=True
        )