import streamlit as st


def download(df):

    st.subheader("Download")

    csv = df.to_csv(index=False).encode()

    st.download_button(

        "Download CSV",

        csv,

        "processed_data.csv",

        "text/csv"

    )