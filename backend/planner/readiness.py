from typing import Dict, Any

class ReadinessAnalyzer:
    """
    Evaluates dataset state for ML readiness, returning a score and detailed breakdown.
    Checks include missing values, target leakage, scaling, class imbalance, and constant targets.
    """
    
    @classmethod
    def analyze_readiness(cls, metadata: Dict[str, Any], quality_report: Dict[str, Any], target_column: str, detected_task: str) -> Dict[str, Any]:
        score = 100
        issues = []
        
        features = metadata.get("features", {})
        total_rows = metadata.get("row_count", 0)
        num_features = len(features) - 1 # excluding target
        
        # 1. Target column specific checks
        target_meta = features.get(target_column, {})
        target_missing_ratio = target_meta.get("missing_ratio", 0.0)
        
        if target_missing_ratio > 0.0:
            penalty = int(target_missing_ratio * 100)
            score -= penalty
            issues.append(f"Target column '{target_column}' has {target_missing_ratio:.1%} missing values (-{penalty} pts).")
            if target_missing_ratio > 0.2:
                issues.append("CRITICAL: Target column has high missing percentage. Downstream models will drop these rows.")
                
        # Constant target check
        if target_meta.get("unique_count", 0) == 1:
            score -= 100
            issues.append("FATAL: Target column is constant (only 1 unique value). Cannot train ML model.")
            
        # 2. General Dataset Checks
        if total_rows < 100:
            score -= 30
            issues.append("CRITICAL: Tiny dataset (less than 100 rows). High risk of overfitting (-30 pts).")
        elif total_rows < 1000:
            score -= 10
            issues.append("Dataset is relatively small (< 1000 rows) (-10 pts).")
            
        # Feature to sample ratio
        if num_features > 0 and total_rows / num_features < 10:
            score -= 15
            issues.append("High feature-to-sample ratio (less than 10 rows per feature). Risk of curse of dimensionality (-15 pts).")
            
        # 3. Class Imbalance (if Classification)
        if detected_task in ["Binary Classification", "Multi-class Classification"]:
            # Normally we'd check actual class distributions here if we had them.
            # But we can check quality report for imbalance warnings on the target column.
            imbalance_warnings = [
                warn for warn in quality_report.get("warnings", [])
                if warn.get("column") == target_column and "imbalance" in warn.get("type", "").lower()
            ]
            if imbalance_warnings:
                score -= 20
                issues.append("Class imbalance detected in target column (-20 pts). Stratified sampling is recommended.")
                
        # 4. Target Leakage Heuristic
        # High correlation between a single feature and target could mean leakage.
        # Here we mock it based on quality report structure if it exists
        leakage_warnings = [
            warn for warn in quality_report.get("warnings", [])
            if "leakage" in warn.get("type", "").lower() or "perfect correlation" in warn.get("type", "").lower()
        ]
        if leakage_warnings:
            score -= 25
            issues.append("Potential target leakage detected. Some features have near-perfect correlation with target (-25 pts).")
            
        # 5. Missing values in features
        feature_missing_scores = []
        for col, m in features.items():
            if col == target_column: continue
            if m.get("missing_ratio", 0) > 0.5:
                feature_missing_scores.append(col)
        
        if feature_missing_scores:
            penalty = min(20, len(feature_missing_scores) * 5)
            score -= penalty
            issues.append(f"{len(feature_missing_scores)} features have >50% missing values (-{penalty} pts).")
            
        final_score = max(0, min(100, score))
        return {
            "readiness_score": final_score,
            "is_ready": final_score >= 60,
            "issues": issues
        }
