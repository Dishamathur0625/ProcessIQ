import pandas as pd


class DataValidator:

    @staticmethod
    def validate(df: pd.DataFrame):
        """
        Validate the uploaded dataset and generate a validation report.
        """

        report = {}

        # -------------------------
        # Basic Validation
        # -------------------------

        if df is None:
            report["valid"] = False
            report["message"] = "No dataset found."
            return report

        if df.empty:
            report["valid"] = False
            report["message"] = "Dataset is empty."
            return report

        # -------------------------
        # Dataset Information
        # -------------------------

        report["valid"] = True
        report["message"] = "Dataset is valid."

        report["rows"] = len(df)
        report["columns"] = len(df.columns)

        report["duplicate_rows"] = int(df.duplicated().sum())

        report["missing_values"] = int(df.isnull().sum().sum())

        report["missing_percentage"] = round(
            (report["missing_values"] / df.size) * 100,
            2
        )

        report["column_names"] = list(df.columns)

        report["dtypes"] = df.dtypes.astype(str).to_dict()

        return report