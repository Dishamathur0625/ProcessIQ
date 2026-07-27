import pandas as pd
from typing import Dict, Any

from backend.engine.core.metrics_engine import MetricsEngine
from backend.engine.profiling.fingerprint import DatasetFingerprint
from backend.engine.profiling.quality_analyzer import QualityDimensionAnalyzer
from backend.engine.profiling.rule_engine import RuleEngine
from backend.engine.profiling.recommendation_engine import RecommendationEngine
from backend.engine.profiling.context_builder import ContextBuilder

class DatasetProfiler:
    """
    Object-oriented dataset profiler acting as the intelligence orchestrator.
    Generates Fingerprints, Quality Dimensions, Issues, and Semantic Context.
    """
    def __init__(self, df: pd.DataFrame, metadata: Dict[str, Any] = None):
        self.df = df
        self.dataset_metadata = metadata or {}
        
        # Modules
        self.recommendation_engine = RecommendationEngine()
        
        # State
        self.fingerprint = ""
        self.metrics = {}
        self.quality_scores = {}
        self.issues = []
        self.recommendations = []
        self.llm_context = ""
        
    def validate(self) -> bool:
        if self.df is None or self.df.empty:
            return False
        return True
        
    def execute_profiling_pipeline(self) -> Dict[str, Any]:
        if not self.validate():
            raise ValueError("Dataset validation failed.")
            
        # 1. Fingerprint
        self.fingerprint = DatasetFingerprint.generate(self.df, self.dataset_metadata)
        
        # 2. Base Metrics
        self.metrics["missing"] = MetricsEngine.calculate_missing(self.df)
        self.metrics["outliers"] = MetricsEngine.calculate_outliers(self.df)
        self.metrics["skew"] = MetricsEngine.calculate_skew(self.df)
        
        # 3. Quality Dimensions (IDRS, PRS, Completeness, etc.)
        self.quality_scores = QualityDimensionAnalyzer.analyze(self.df, self.metrics)
        self.metrics["duplicate_percentage"] = (self.df.duplicated().sum() / len(self.df)) * 100 if len(self.df) > 0 else 0.0
        
        # 4. Rule Engine (Issues & Severities)
        self.issues = RuleEngine.evaluate(self.metrics)
        
        # 5. Recommendation Engine
        self.recommendations = self.recommendation_engine.generate_recommendations(self.issues)
        
        # 6. Context Builder
        self.llm_context = ContextBuilder.build_context(
            self.fingerprint, 
            self.quality_scores, 
            self.issues, 
            self.recommendations
        )
        
        return {
            "fingerprint": self.fingerprint,
            "quality_scores": self.quality_scores,
            "issues": [i.model_dump() for i in self.issues],
            "recommendations": [r.model_dump() for r in self.recommendations],
            "llm_context": self.llm_context
        }
