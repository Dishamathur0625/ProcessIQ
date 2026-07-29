import pandas as pd
from pathlib import Path


class FileLoader:

    SUPPORTED_EXTENSIONS = [".csv", ".xlsx", ".xls"]

    @staticmethod
    def load(file):
        """
        Load CSV, XLS or XLSX files into a Pandas DataFrame.
        """

        extension = Path(file.name).suffix.lower()

        if extension not in FileLoader.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {extension}"
            )

        try:

            if extension == ".csv":
                df = pd.read_csv(file)

            else:
                df = pd.read_excel(file)

            if df.empty:
                raise ValueError("Uploaded file is empty.")

            return df

        except Exception as e:
            raise Exception(
                f"Failed to load file.\n{e}"
            )