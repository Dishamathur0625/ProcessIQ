from typing import List, Dict, Any

class ModelRecommender:
    """
    Rule-based engine for recommending ML models based on the detected task and dataset heuristics.
    """
    
    MODELS = {
        "Regression": [
            {"id": "lr", "name": "Linear Regression", "cost": "Low", "interpretability": "High", "base_score": 50},
            {"id": "rf_reg", "name": "Random Forest", "cost": "Medium", "interpretability": "Medium", "base_score": 70},
            {"id": "xgb_reg", "name": "XGBoost", "cost": "High", "interpretability": "Medium", "base_score": 80},
            {"id": "lgb_reg", "name": "LightGBM", "cost": "Medium", "interpretability": "Medium", "base_score": 75},
            {"id": "cat_reg", "name": "CatBoost", "cost": "High", "interpretability": "Medium", "base_score": 75},
        ],
        "Binary Classification": [
            {"id": "lr_clf", "name": "Logistic Regression", "cost": "Low", "interpretability": "High", "base_score": 50},
            {"id": "rf_clf", "name": "Random Forest", "cost": "Medium", "interpretability": "Medium", "base_score": 70},
            {"id": "xgb_clf", "name": "XGBoost", "cost": "High", "interpretability": "Medium", "base_score": 80},
            {"id": "lgb_clf", "name": "LightGBM", "cost": "Medium", "interpretability": "Medium", "base_score": 75},
            {"id": "cat_clf", "name": "CatBoost", "cost": "High", "interpretability": "Medium", "base_score": 75},
        ],
        "Multi-class Classification": [
            {"id": "rf_multi", "name": "Random Forest", "cost": "Medium", "interpretability": "Medium", "base_score": 70},
            {"id": "xgb_multi", "name": "XGBoost", "cost": "High", "interpretability": "Medium", "base_score": 80},
            {"id": "lgb_multi", "name": "LightGBM", "cost": "Medium", "interpretability": "Medium", "base_score": 75},
            {"id": "cat_multi", "name": "CatBoost", "cost": "High", "interpretability": "Medium", "base_score": 75},
        ]
    }
    
    @classmethod
    def recommend(cls, task: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        candidates = cls.MODELS.get(task, [])
        if not candidates:
            return []
            
        features = metadata.get("features", {})
        total_rows = metadata.get("row_count", 0)
        
        # Count categorical features
        categorical_count = sum(
            1 for m in features.values() 
            if m.get("inferred_type") in ["categorical", "string"] and not m.get("is_identifier")
        )
        
        recommendations = []
        for model in candidates:
            score = model["base_score"]
            breakdown = [f"Base score: {score}"]
            
            # Rule 1: Dataset size
            if total_rows > 100000:
                if "LightGBM" in model["name"]:
                    score += 20
                    breakdown.append("Large dataset: +20 (LightGBM excels on large data)")
                elif "XGBoost" in model["name"]:
                    score += 15
                    breakdown.append("Large dataset: +15 (XGBoost scales well)")
                elif "Random Forest" in model["name"]:
                    score -= 10
                    breakdown.append("Large dataset: -10 (RF memory usage high)")
            elif total_rows < 1000:
                if "Random Forest" in model["name"]:
                    score += 15
                    breakdown.append("Small dataset: +15 (RF robust to overfitting)")
                elif "Linear" in model["name"] or "Logistic" in model["name"]:
                    score += 20
                    breakdown.append("Small dataset: +20 (Linear models resist overfitting)")
                elif "XGBoost" in model["name"] or "LightGBM" in model["name"]:
                    score -= 10
                    breakdown.append("Small dataset: -10 (Gradient boosting risks overfitting)")
                    
            # Rule 2: Categorical Features
            if categorical_count > 5:
                if "CatBoost" in model["name"]:
                    score += 25
                    breakdown.append(f"Many categoricals ({categorical_count}): +25 (CatBoost handles naturally)")
                elif "LightGBM" in model["name"]:
                    score += 10
                    breakdown.append(f"Many categoricals: +10 (LightGBM has native support)")
                    
            # Bound score
            final_score = max(0, min(100, score))
            
            recommendations.append({
                "model_name": model["name"],
                "model_id": model["id"],
                "suitability_score": final_score,
                "computational_cost": model["cost"],
                "interpretability": model["interpretability"],
                "score_breakdown": breakdown
            })
            
        # Sort by score descending
        return sorted(recommendations, key=lambda x: x["suitability_score"], reverse=True)
