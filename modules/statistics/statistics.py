import pandas as pd


class Statistics:

    @staticmethod
    def generate(df: pd.DataFrame):

        summary = {}

        summary["rows"] = len(df)

        summary["columns"] = len(df.columns)

        total_cells = df.shape[0] * df.shape[1]

        missing = df.isnull().sum().sum()

        summary["missing"] = int(missing)

        summary["missing_percentage"] = round(
            (missing / total_cells) * 100,
            2
        )

        summary["duplicate_rows"] = int(
            df.duplicated().sum()
        )

        summary["numeric_columns"] = len(
            df.select_dtypes(include="number").columns
        )

        summary["categorical_columns"] = len(
            df.select_dtypes(exclude="number").columns
        )

        return summary

    @staticmethod
    def variable_summary(df):

        numeric = df.select_dtypes(include="number")

        result = pd.DataFrame({

            "Type": df.dtypes.astype(str),

            "Missing":

            df.isnull().sum(),

            "Missing %":

            round(df.isnull().mean()*100,2)

        })

        if len(numeric.columns):

            result["Mean"] = numeric.mean()

            result["Median"] = numeric.median()

            result["Std"] = numeric.std()

            result["Min"] = numeric.min()

            result["Max"] = numeric.max()

        return result

    @staticmethod
    def missing_values(df):

        result = pd.DataFrame({

            "Column": df.columns,

            "Missing Values": df.isnull().sum().values,

            "Missing %": (
                df.isnull().mean()*100
            ).round(2).values

        })

        return result