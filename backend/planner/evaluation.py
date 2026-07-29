from typing import Dict, Any

class EvaluationPlanner:
    """
    Generates deterministic evaluation strategies including Train/Test split,
    Cross Validation strategy, and Evaluation Metrics based on task and dataset state.
    """
    
    @classmethod
    def plan(cls, task: str, readiness_info: Dict[str, Any]) -> Dict[str, Any]:
        issues = readiness_info.get("issues", [])
        has_imbalance = any("imbalance" in i.lower() for i in issues)
        
        strategy = {
            "train_test_split": "80/20",
            "cross_validation": "5-Fold CV",
            "metrics": []
        }
        
        if task == "Regression":
            strategy["metrics"] = ["RMSE", "MAE", "R2"]
            
        elif task == "Binary Classification":
            strategy["metrics"] = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
            if has_imbalance:
                strategy["metrics"].append("PR-AUC")
                strategy["cross_validation"] = "Stratified 5-Fold CV"
                
        elif task == "Multi-class Classification":
            strategy["metrics"] = ["Accuracy", "Macro F1", "Weighted F1"]
            if has_imbalance:
                strategy["cross_validation"] = "Stratified 5-Fold CV"
                
        return strategy
