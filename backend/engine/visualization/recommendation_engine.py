import pandas as pd
from typing import List, Dict, Any, Tuple
import numpy as np

class VisualizationRecommendationEngine:
    """
    Decides the optimal visualization given a set of columns and their metadata.
    """
    
    @staticmethod
    def recommend(df: pd.DataFrame, columns: List[str]) -> Tuple[str, str]:
        """
        Returns (chart_type, purpose).
        """
        if len(columns) == 1:
            col = columns[0]
            if pd.api.types.is_numeric_dtype(df[col]):
                # Check cardinality to see if it's acting like a category
                if df[col].nunique() < 15:
                    return "bar", "Categorical Distribution"
                
                # Check for outliers
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[col][(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                
                if len(outliers) > 0:
                    return "box", "Outlier Detection"
                
                return "histogram", "Distribution"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                return "histogram", "Time Distribution"
            else:
                # Categorical
                if df[col].nunique() > 20:
                    return "treemap", "High Cardinality Category"
                return "bar", "Category Counts"
                
        elif len(columns) == 2:
            col1, col2 = columns[0], columns[1]
            is_num1 = pd.api.types.is_numeric_dtype(df[col1])
            is_num2 = pd.api.types.is_numeric_dtype(df[col2])
            is_cat1 = not is_num1 and not pd.api.types.is_datetime64_any_dtype(df[col1])
            is_cat2 = not is_num2 and not pd.api.types.is_datetime64_any_dtype(df[col2])
            is_date1 = pd.api.types.is_datetime64_any_dtype(df[col1])
            is_date2 = pd.api.types.is_datetime64_any_dtype(df[col2])
            
            if is_num1 and is_num2:
                return "scatter", "Numeric Relationship"
                
            if (is_date1 and is_num2) or (is_date2 and is_num1):
                return "line", "Time Series Trend"
                
            if (is_cat1 and is_num2) or (is_cat2 and is_num1):
                return "box", "Category Distribution"
                
            if is_cat1 and is_cat2:
                return "heatmap", "Categorical Correlation"
                
        else:
            # > 2 columns
            num_cols = [c for c in columns if pd.api.types.is_numeric_dtype(df[c])]
            if len(num_cols) == len(columns):
                return "heatmap", "Correlation Matrix"
            
            # Default fallback for multivariate
            return "parallel_coordinates", "Multivariate Analysis"
            
        return "table", "Raw Data View"
