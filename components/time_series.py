import streamlit as st
import plotly.express as px
import pandas as pd


def time_series(df):

    st.subheader("Time Series Trend")

    numeric = df.select_dtypes(include="number").columns.tolist()

    if len(numeric) == 0:
        st.info("No numeric columns found.")
        return

    x = df.columns[0]

    fig = px.line(
        df,
        x=x,
        y=numeric[:3]
    )

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )