import pandas as pd
from typing import Dict, Any

class ModelReadinessReportGenerator:
    """
    Evaluates the final dataset to determine if it is mathematically and structurally
    ready to be ingested by a Machine Learning model.
    """
    
    @staticmethod
    def generate(df: pd.DataFrame, target_variable: str = None) -> str:
        md = ["# ProcessIQ Model Readiness Report\n"]
        md.append("This document evaluates the structural integrity of the final Analytics Engine output "
                  "and certifies its readiness for predictive modeling.\n")
                  
        md.append("## 1. Dataset Shape & Footprint\n")
        md.append(f"- **Rows:** {len(df)}")
        md.append(f"- **Columns (Features):** {len(df.columns)}")
        mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        md.append(f"- **Memory Footprint:** {mem_mb:.2f} MB\n")
        
        md.append("## 2. Readiness Checklist\n")
        
        # 1. Missing Values
        missing = df.isna().sum().sum()
        if missing == 0:
            md.append("- [x] **Missing Values Cleared:** 0 missing values detected. (Perfect)")
        else:
            md.append(f"- [ ] **Missing Values Detected:** {missing} missing values remain. (Action Required)")
            
        # 2. Categorical Encoding
        cat_cols = df.select_dtypes(exclude=['number', 'datetime']).columns.tolist()
        if len(cat_cols) == 0:
            md.append("- [x] **Categorical Features Encoded:** All features are purely numeric. (Perfect)")
        else:
            md.append(f"- [ ] **Unencoded Categoricals:** {len(cat_cols)} categorical columns detected. (Action Required)")
            
        # 3. Target Variable
        is_classification = False
        if target_variable and target_variable in df.columns:
            target_data = df[target_variable]
            md.append(f"- [x] **Target Variable Present:** `{target_variable}`")
            # Heuristic for ML task
            if pd.api.types.is_numeric_dtype(target_data) and target_data.nunique() > 15:
                task = "Regression"
            else:
                task = "Classification"
                is_classification = True
            md.append(f"- [x] **Predicted ML Task:** {task}")
        else:
            md.append("- [ ] **Target Variable:** Not specified or missing. Cannot recommend supervised ML task.")
            
        md.append("\n## 3. Final Certification\n")
        if missing == 0 and len(cat_cols) == 0 and target_variable in df.columns:
            md.append("> **✅ CERTIFIED READY FOR MACHINE LEARNING**\n")
            md.append("The dataset has passed all foundational requirements. It is clean, numeric, and fully traceable.")
            
            md.append("\n### Recommended Next Steps in ProcessIQ:\n")
            if is_classification:
                md.append("1. Pass to **Prediction Planner (Phase 12)** for model selection.")
                md.append("2. We recommend starting with **XGBoost Classifier** or **Random Forest Classifier**.")
            else:
                md.append("1. Pass to **Prediction Planner (Phase 12)** for model selection.")
                md.append("2. We recommend starting with **XGBoost Regressor** or **Ridge Regression**.")
        else:
            md.append("> **❌ NOT READY FOR MACHINE LEARNING**\n")
            md.append("The dataset still contains structural flaws (missing values or string columns). "
                      "Please route the dataset back through the Cleaning and Engineering pipelines.")
            
        return "\n".join(md)
