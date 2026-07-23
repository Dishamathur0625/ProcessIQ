import streamlit as st


def top_bar(file_name=None, rows=None, columns=None, time_range=None):

    c1, c2, c3, c4, c5 = st.columns([2.2, 1.5, 1, 1, 2.8])

    with c1:

        st.markdown(
            f"""
            <div class='metric-card'>
            <b>📄 File</b><br>
            {file_name if file_name else "No file uploaded"}
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.success("Processed Successfully")

    with c3:

        st.metric(
            "Rows",
            rows if rows else "-"
        )

    with c4:

        st.metric(
            "Columns",
            columns if columns else "-"
        )

    with c5:

        st.markdown(
            f"""
            <div class='metric-card'>
            <b>⏱ Time Range</b><br>
            {time_range if time_range else "--"}
            </div>
            """,
            unsafe_allow_html=True
        )