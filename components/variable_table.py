import streamlit as st
import pandas as pd


def variable_table(df):

    st.subheader("Variable Overview")

    summary = []

    for col in df.columns:

        dtype = str(df[col].dtype)

        missing = round(df[col].isna().mean() * 100, 2)

        if pd.api.types.is_numeric_dtype(df[col]):

            mean = round(df[col].mean(), 2)

            std = round(df[col].std(), 2)

            minimum = round(df[col].min(), 2)

            maximum = round(df[col].max(), 2)

        else:

            mean = "-"

            std = "-"

            minimum = "-"

            maximum = "-"

        summary.append({

            "Variable": col,

            "Type": dtype,

            "Missing %": missing,

            "Mean": mean,

            "Std Dev": std,

            "Min": minimum,

            "Max": maximum

        })

    st.dataframe(

        pd.DataFrame(summary),

        use_container_width=True,

        height=330

    )