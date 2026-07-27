import pandas as pd
import numpy as np
from typing import List, Optional
from backend.engine.visualization.schemas import Insight

class InsightGenerator:
    """
    Analyzes the specific data used for a visualization and returns a structured Insight.
    """
    
    @staticmethod
    def generate_for_distribution(df: pd.DataFrame, column: str) -> Optional[Insight]:
        if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
            return None
            
        data = df[column].dropna()
        if data.empty:
            return None
            
        skewness = data.skew()
        
        if skewness > 1.0:
            finding = f"Right-skew detected in {column}"
            evidence = f"Skewness = {skewness:.2f}"
            impact = "Model may underestimate higher values."
            recommendation = "Consider applying a log-transform or Box-Cox transform."
        elif skewness < -1.0:
            finding = f"Left-skew detected in {column}"
            evidence = f"Skewness = {skewness:.2f}"
            impact = "Model may underestimate lower values."
            recommendation = "Consider applying a power transform."
        else:
            finding = f"Normal distribution approximated for {column}"
            evidence = f"Skewness = {skewness:.2f}"
            impact = "Ideal for linear models."
            recommendation = "No transformation needed."
            
        return Insight(
            finding=finding,
            evidence=evidence,
            impact=impact,
            recommendation=recommendation
        )
        
    @staticmethod
    def generate_for_correlation(df: pd.DataFrame, col1: str, col2: str) -> Optional[Insight]:
        if col1 not in df.columns or col2 not in df.columns:
            return None
            
        data1 = df[col1]
        data2 = df[col2]
        
        if not pd.api.types.is_numeric_dtype(data1) or not pd.api.types.is_numeric_dtype(data2):
            return None
            
        corr = data1.corr(data2)
        
        if abs(corr) > 0.85:
            finding = f"Strong correlation between {col1} and {col2}"
            evidence = f"Pearson r = {corr:.2f}"
            impact = "Potential multicollinearity detected."
            recommendation = "Consider removing one feature or applying PCA."
        elif abs(corr) > 0.5:
            finding = f"Moderate correlation between {col1} and {col2}"
            evidence = f"Pearson r = {corr:.2f}"
            impact = "Features share some variance."
            recommendation = "Both features can likely be safely kept."
        else:
            finding = f"Weak or no correlation between {col1} and {col2}"
            evidence = f"Pearson r = {corr:.2f}"
            impact = "Features provide independent signals."
            recommendation = "Keep both features for modeling."
            
        return Insight(
            finding=finding,
            evidence=evidence,
            impact=impact,
            recommendation=recommendation
        )
        
    @staticmethod
    def generate_for_outliers(df: pd.DataFrame, column: str) -> Optional[Insight]:
        if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
            return None
            
        data = df[column].dropna()
        if data.empty:
            return None
            
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        outlier_count = len(outliers)
        
        if outlier_count > 0:
            finding = f"Statistical outliers detected in {column}"
            evidence = f"{outlier_count} outliers found (>{upper_bound:.2f} or <{lower_bound:.2f})"
            impact = "May skew distance-based algorithms and linear regression."
            recommendation = "Consider Winsorization or Robust Scaler."
            
            return Insight(
                finding=finding,
                evidence=evidence,
                impact=impact,
                recommendation=recommendation
            )
        
        return None
