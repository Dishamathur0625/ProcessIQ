import streamlit as st


def preview_table(df):

    st.subheader("Data Preview")

    st.dataframe(

        df.head(),

        use_container_width=True,

        height=330

    )