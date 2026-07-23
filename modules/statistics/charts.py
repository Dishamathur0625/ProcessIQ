import pandas as pd
import plotly.express as px


class Charts:

    @staticmethod
    def histogram(df, column):

        fig = px.histogram(
            df,
            x=column,
            nbins=30,
            title=f"{column} Distribution"
        )

        fig.update_layout(
            template="plotly_white",
            height=450
        )

        return fig

    @staticmethod
    def boxplot(df):

        numeric = df.select_dtypes(include="number")

        fig = px.box(
            numeric,
            title="Box Plot"
        )

        fig.update_layout(
            template="plotly_white",
            height=450
        )

        return fig

    @staticmethod
    def line_chart(df, x, y):

        fig = px.line(
            df,
            x=x,
            y=y,
            title=f"{y} Trend"
        )

        fig.update_layout(
            template="plotly_white",
            height=450
        )

        return fig

    @staticmethod
    def missing_chart(df):

        missing = (
            df.isnull()
            .sum()
            .reset_index()
        )

        missing.columns = [
            "Column",
            "Missing"
        ]

        fig = px.bar(
            missing,
            x="Column",
            y="Missing",
            title="Missing Values"
        )

        fig.update_layout(
            template="plotly_white",
            height=450
        )

        return fig