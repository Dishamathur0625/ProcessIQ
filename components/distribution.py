import streamlit as st
import plotly.express as px


def distribution(df):

    st.subheader("Variable Distribution")

    numeric = df.select_dtypes(include="number").columns.tolist()

    if len(numeric) == 0:
        st.info("No numeric columns")
        return

    column = st.selectbox(
        "Variable",
        numeric,
        key="hist"
    )

    fig = px.histogram(
        df,
        x=column,
        nbins=30
    )

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )