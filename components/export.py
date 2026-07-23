import streamlit as st
import pandas as pd
from io import BytesIO


def export_module(df):

    st.subheader("📥 Export Data")

    if df is None or df.empty:
        st.warning("No data available for export.")
        return

    # -----------------------------
    # CSV Export
    # -----------------------------
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download Cleaned Data (CSV)",
        data=csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        use_container_width=True
    )

    # -----------------------------
    # Excel Export
    # -----------------------------
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Processed Data", index=False)

    excel_data = output.getvalue()

    st.download_button(
        label="⬇ Download Cleaned Data (Excel)",
        data=excel_data,
        file_name="cleaned_dataset.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # -----------------------------
    # Statistics Export
    # -----------------------------
    stats = df.describe(include="all").transpose()

    output_stats = BytesIO()

    with pd.ExcelWriter(output_stats, engine="openpyxl") as writer:
        stats.to_excel(writer, sheet_name="Statistics")

    stats_excel = output_stats.getvalue()

    st.download_button(
        label="⬇ Download Statistics Report",
        data=stats_excel,
        file_name="statistics_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )