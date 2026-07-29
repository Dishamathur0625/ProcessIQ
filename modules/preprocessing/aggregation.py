import pandas as pd


class TimeAggregation:

    SUPPORTED_METHODS = {
        "Mean": "mean",
        "Median": "median",
        "Max": "max",
        "Min": "min",
        "Sum": "sum"
    }

    POSSIBLE_TIMESTAMP_COLUMNS = [
        "datetime",
        "date_time",
        "timestamp",
        "time",
        "date"
    ]

    @staticmethod
    def aggregate(
        df: pd.DataFrame,
        interval: str,
        method: str = "Mean"
    ):

        report = {}

        timestamp_column = None

        # -------------------------
        # Detect Timestamp Column
        # -------------------------
        for column in df.columns:

            if column.lower() in TimeAggregation.POSSIBLE_TIMESTAMP_COLUMNS:

                timestamp_column = column
                break

        if timestamp_column is None:
            raise ValueError(
                "Timestamp column not found."
            )

        # -------------------------
        # Convert Timestamp
        # -------------------------
        df[timestamp_column] = pd.to_datetime(
            df[timestamp_column],
            errors="coerce"
        )

        df = df.dropna(subset=[timestamp_column])

        df = df.set_index(timestamp_column)

        # -------------------------
        # Numeric Columns Only
        # -------------------------
        numeric_df = df.select_dtypes(include="number")

        aggregation_function = TimeAggregation.SUPPORTED_METHODS.get(
            method,
            "mean"
        )

        aggregated_df = getattr(
            numeric_df.resample(interval),
            aggregation_function
        )()

        aggregated_df = aggregated_df.reset_index()

        # -------------------------
        # Report
        # -------------------------
        report["interval"] = interval
        report["method"] = method
        report["input_rows"] = len(df)
        report["output_rows"] = len(aggregated_df)

        return aggregated_df, report