import pandas as pd
import uuid
import json
from typing import List, Dict, Any, Optional

import plotly.express as px
import plotly.graph_objects as go
import plotly.utils

from backend.engine.visualization.schemas import VisualizationSpecification
from backend.engine.visualization.recommendation_engine import VisualizationRecommendationEngine
from backend.engine.visualization.insight_generator import InsightGenerator

class VisualizationSpecificationGenerator:
    """
    Factory that generates theme-agnostic VisualizationSpecification objects
    containing Plotly JSON, metadata, and insights.
    """
    
    @staticmethod
    def _create_plotly_json(fig: go.Figure) -> Dict[str, Any]:
        """Convert Plotly figure to a JSON serializable dict."""
        # Clean layout to be theme agnostic
        fig.update_layout(
            template="plotly_white", # Neutral starting point
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return json.loads(json.dumps(fig.to_dict(), cls=plotly.utils.PlotlyJSONEncoder))
        
    @staticmethod
    def generate_spec(df: pd.DataFrame, columns: List[str], priority: int = 1) -> Optional[VisualizationSpecification]:
        if df.empty or not columns:
            return None
            
        chart_type, purpose = VisualizationRecommendationEngine.recommend(df, columns)
        
        fig = None
        insight = None
        hints = ["Zoom", "Pan", "Hover"]
        
        try:
            if chart_type == "histogram":
                fig = px.histogram(df, x=columns[0], marginal="box", opacity=0.8)
                insight = InsightGenerator.generate_for_distribution(df, columns[0])
                hints.append("Brush")
                
            elif chart_type == "scatter":
                # Sample if too large
                plot_df = df.sample(min(len(df), 2000)) if len(df) > 2000 else df
                fig = px.scatter(plot_df, x=columns[0], y=columns[1], opacity=0.7)
                insight = InsightGenerator.generate_for_correlation(plot_df, columns[0], columns[1])
                hints.append("Lasso")
                
            elif chart_type == "box":
                if len(columns) == 1:
                    fig = px.box(df, y=columns[0])
                    insight = InsightGenerator.generate_for_outliers(df, columns[0])
                else:
                    # One categorical, one numeric
                    cat_col = columns[0] if not pd.api.types.is_numeric_dtype(df[columns[0]]) else columns[1]
                    num_col = columns[1] if cat_col == columns[0] else columns[0]
                    fig = px.box(df, x=cat_col, y=num_col)
                    
            elif chart_type == "heatmap":
                corr = df[columns].corr()
                fig = px.imshow(corr, text_auto=True, aspect="auto")
                if len(columns) == 2:
                    insight = InsightGenerator.generate_for_correlation(df, columns[0], columns[1])
                    
            elif chart_type == "bar":
                val_counts = df[columns[0]].value_counts().reset_index()
                val_counts.columns = [columns[0], 'count']
                fig = px.bar(val_counts, x=columns[0], y='count')
                
            elif chart_type == "line":
                plot_df = df.sort_values(by=columns[0]) if pd.api.types.is_datetime64_any_dtype(df[columns[0]]) else df.sort_values(by=columns[1])
                x_col = columns[0] if pd.api.types.is_datetime64_any_dtype(df[columns[0]]) else columns[1]
                y_col = columns[1] if x_col == columns[0] else columns[0]
                fig = px.line(plot_df, x=x_col, y=y_col)
                hints.extend(["RangeSlider"])
                
            else:
                return None
                
            if fig is None:
                return None
                
            return VisualizationSpecification(
                chart_id=str(uuid.uuid4()),
                chart_type=chart_type,
                columns_used=columns,
                purpose=purpose,
                insight=insight,
                interaction_hints=hints,
                required_filters=[],
                estimated_render_cost="High" if len(df) > 50000 else "Medium" if len(df) > 5000 else "Low",
                priority=priority,
                theme="default",
                supports_dark_mode=True,
                plotly_json=VisualizationSpecificationGenerator._create_plotly_json(fig)
            )
            
        except Exception as e:
            # Silently fail visualization generation to not break pipeline
            print(f"Warning: Failed to generate visualization for {columns}: {str(e)}")
            return None
            
    @staticmethod
    def generate_suite_for_dataset(df: pd.DataFrame, target_variable: str = None) -> List[VisualizationSpecification]:
        """
        Generates a suite of optimal visualizations for a given dataset automatically.
        """
        specs = []
        
        # 1. Target Distribution (Highest Priority)
        if target_variable and target_variable in df.columns:
            spec = VisualizationSpecificationGenerator.generate_spec(df, [target_variable], priority=10)
            if spec: specs.append(spec)
            
        # 2. Correlation Heatmap (If we have enough numerics)
        num_cols = df.select_dtypes(include='number').columns.tolist()
        if len(num_cols) > 1:
            # Top 10 max
            plot_cols = num_cols[:min(10, len(num_cols))]
            spec = VisualizationSpecificationGenerator.generate_spec(df, plot_cols, priority=8)
            if spec: specs.append(spec)
            
        # 3. Target vs Top Features
        if target_variable and target_variable in df.columns and len(num_cols) > 1:
            # Find a feature with high variance to plot against target
            variances = df[num_cols].var().sort_values(ascending=False)
            top_var_col = [c for c in variances.index if c != target_variable]
            if top_var_col:
                spec = VisualizationSpecificationGenerator.generate_spec(df, [target_variable, top_var_col[0]], priority=7)
                if spec: specs.append(spec)
                
        # 4. Outlier Highlights
        for col in num_cols[:3]: # Limit to top 3 to save time
            if col != target_variable:
                spec = VisualizationSpecificationGenerator.generate_spec(df, [col], priority=5)
                if spec: specs.append(spec)
                
        return specs
