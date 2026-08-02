import pandas as pd
import os
import traceback

class CodeExecutor:
    """
    Executes dynamically generated pandas code in a restricted local scope.
    """
    
    @staticmethod
    def execute_on_df(code: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Executes dynamically generated pandas code against an in-memory dataframe.
        The generated code expects a pandas DataFrame named `df` and must modify
        or reassign it.
        """
        local_vars = {"df": df, "pd": pd}
        global_vars = {"__builtins__": __builtins__}

        exec(code, global_vars, local_vars)

        modified_df = local_vars.get("df")
        if not isinstance(modified_df, pd.DataFrame):
            raise ValueError("The executed code did not result in a valid pandas DataFrame named 'df'.")
        return modified_df

    @staticmethod
    def execute(code: str, input_path: str, output_path: str) -> bool:
        """
        Loads the dataset, executes the code, and saves the result.
        The generated code expects a pandas DataFrame named `df`.
        """
        try:
            # Load the dataset
            if input_path.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(input_path)
            elif input_path.lower().endswith(".csv"):
                df = pd.read_csv(input_path)
            else:
                raise ValueError("Unsupported file format for execution.")

            modified_df = CodeExecutor.execute_on_df(code, df)

            # Save the result
            if output_path.lower().endswith(".xlsx"):
                modified_df.to_excel(output_path, index=False)
            elif output_path.lower().endswith(".csv"):
                modified_df.to_csv(output_path, index=False)
            else:
                # Default to saving as xlsx if no valid extension
                modified_df.to_excel(output_path + ".xlsx", index=False)

            return True
        except Exception as e:
            print(f"Error executing dynamic code: {e}")
            print(traceback.format_exc())
            raise Exception(f"Execution failed: {str(e)}")
