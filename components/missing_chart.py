import streamlit as st
import plotly.express as px


def missing_chart(df):

    st.subheader("Missing Values %")

    missing = (

        df.isna()

        .mean()

        .mul(100)

        .sort_values(ascending=False)

    )

    fig = px.bar(

        x=missing.values,

        y=missing.index,

        orientation="h",

        labels={

            "x": "Missing %",

            "y": ""

        }

    )

    fig.update_layout(

        height=330,

        margin=dict(

            l=10,

            r=10,

            t=20,

            b=20

        )

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )