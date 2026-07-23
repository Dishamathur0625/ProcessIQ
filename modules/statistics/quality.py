import pandas as pd


class DataQuality:

    @staticmethod
    def calculate(df: pd.DataFrame):

        report = {}

        total_cells = df.shape[0] * df.shape[1]

        # -----------------------------
        # Missing Values
        # -----------------------------
        missing = df.isnull().sum().sum()

        completeness = (
            (total_cells - missing) / total_cells
        ) * 100

        # -----------------------------
        # Duplicate Rows
        # -----------------------------
        duplicates = df.duplicated().sum()

        uniqueness = (
            (len(df) - duplicates) / len(df)
        ) * 100

        # -----------------------------
        # Overall Score
        # -----------------------------
        score = round(
            (completeness + uniqueness) / 2,
            2
        )

        if score >= 95:
            rating = "Excellent"

        elif score >= 85:
            rating = "Good"

        elif score >= 70:
            rating = "Average"

        else:
            rating = "Poor"

        report["score"] = score
        report["rating"] = rating
        report["completeness"] = round(completeness, 2)
        report["uniqueness"] = round(uniqueness, 2)

        return report