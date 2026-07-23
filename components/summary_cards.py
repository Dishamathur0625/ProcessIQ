import streamlit as st


def summary_cards(rows, columns, missing, quality):

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "TOTAL ROWS",
            f"{rows:,}"
        )

    with c2:

        st.metric(
            "TOTAL COLUMNS",
            columns
        )

    with c3:

        st.metric(
            "MISSING VALUES",
            missing
        )

    with c4:

        st.metric(
            "DATA QUALITY",
            f"{quality:.2f}%"
        )