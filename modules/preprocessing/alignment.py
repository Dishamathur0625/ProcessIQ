import pandas as pd


class DataAlignment:

    POSSIBLE_TIMESTAMP_COLUMNS = [
        "datetime",
        "date_time",
        "timestamp",
        "time",
        "date"
    ]

    @staticmethod
    def clean(df: pd.DataFrame):

        report = {}

        original_rows = len(df)
        original_columns = len(df.columns)

        # -------------------------
        # Remove empty rows
        # -------------------------
        df = df.dropna(how="all")

        # -------------------------
        # Remove empty columns
        # -------------------------
        df = df.dropna(axis=1, how="all")

        # -------------------------
        # Remove duplicate rows
        # -------------------------
        duplicate_rows = df.duplicated().sum()

        df = df.drop_duplicates()

        # -------------------------
        # Clean column names
        # -------------------------
        df.columns = (
            df.columns
            .str.strip()
            .str.replace(" ", "_")
        )

        # -------------------------
        # Detect timestamp column
        # -------------------------
        timestamp_column = None

        for column in df.columns:

            if column.lower() in DataAlignment.POSSIBLE_TIMESTAMP_COLUMNS:

                timestamp_column = column
                break

        # -------------------------
        # Convert timestamp
        # -------------------------
        if timestamp_column:

            df[timestamp_column] = pd.to_datetime(
                df[timestamp_column],
                errors="coerce"
            )

            df = df.dropna(subset=[timestamp_column])

            df = df.sort_values(timestamp_column)

        # -------------------------
        # Reset Index
        # -------------------------
        df = df.reset_index(drop=True)

        # -------------------------
        # Alignment Report
        # -------------------------
        report["original_rows"] = original_rows
        report["processed_rows"] = len(df)

        report["original_columns"] = original_columns
        report["processed_columns"] = len(df.columns)

        report["duplicates_removed"] = int(duplicate_rows)

        report["timestamp_column"] = timestamp_column

        return df, report