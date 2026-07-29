import io
import pandas as pd


class ExcelExporter:

    @staticmethod
    def export(df: pd.DataFrame):

        output = io.BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                sheet_name="Processed Data",
                index=False
            )

        output.seek(0)

        return output