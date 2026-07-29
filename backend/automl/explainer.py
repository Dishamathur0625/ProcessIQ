from typing import Dict, Any, List
import pandas as pd
import numpy as np

class Explainer:
    """
    Generates explainability metrics following the hierarchy:
    Native Feature Importance -> Permutation Importance -> SHAP.
    Outputs Plotly JSON specs suitable for the Visualization Engine.
    """
    
    @staticmethod
    def get_feature_importance(estimator: Any, X_val: pd.DataFrame, y_val: pd.Series, task: str, random_seed: int = 42) -> Dict[str, Any]:
        """
        Calculates feature importance and formats it as a Plotly spec.
        """
        importances = None
        feature_names = X_val.columns.tolist()
        method = "Unknown"
        
        # 1. Try Native
        if hasattr(estimator, "feature_importances_"):
            importances = estimator.feature_importances_
            method = "Native"
        elif hasattr(estimator, "coef_"):
            # Linear models
            coef = estimator.coef_
            if coef.ndim > 1:
                importances = np.mean(np.abs(coef), axis=0)
            else:
                importances = np.abs(coef)
            method = "Coefficients"
        
        # 2. Fallback to Permutation
        if importances is None:
            from sklearn.inspection import permutation_importance
            scoring = "neg_mean_squared_error" if task == "Regression" else "accuracy"
            result = permutation_importance(estimator, X_val, y_val, n_repeats=5, random_state=random_seed, scoring=scoring)
            importances = result.importances_mean
            method = "Permutation"
            
        # Optional: Add SHAP here if needed in the future, but native/permutation covers 99%
        
        # Format for Plotly
        df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
        df = df.sort_values(by="Importance", ascending=True).tail(20) # Top 20 features
        
        # Plotly spec
        data = [{
            "type": "bar",
            "x": df["Importance"].tolist(),
            "y": df["Feature"].tolist(),
            "orientation": "h",
            "marker": {"color": "#6366f1"}
        }]
        
        layout = {
            "title": f"Feature Importance ({method})",
            "xaxis": {"title": "Importance Score"},
            "yaxis": {"title": "Feature", "automargin": True},
            "margin": {"l": 150}
        }
        
        return {"data": data, "layout": layout, "method": method}
