import streamlit as st
import plotly.express as px


def boxplot(df):

    st.subheader("Box Plot")

    numeric = df.select_dtypes(include="number").columns.tolist()

    if len(numeric) == 0:
        st.info("No numeric columns")
        return

    fig = px.box(
        df[numeric]
    )

    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )