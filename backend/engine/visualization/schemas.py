from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Insight(BaseModel):
    """
    Structured insight generated from data to feed into the Copilot and UI.
    """
    finding: str
    evidence: str
    impact: str
    recommendation: str

class VisualizationSpecification(BaseModel):
    """
    Metadata-driven specification for a chart.
    The frontend reads this and renders the actual Plotly/D3 chart using the provided JSON.
    """
    chart_id: str
    chart_type: str
    columns_used: List[str]
    purpose: str
    
    insight: Optional[Insight] = None
    
    interaction_hints: List[str] = ["Zoom", "Hover"]
    required_filters: List[str] = []
    
    estimated_render_cost: str = "Low"
    priority: int = 1
    
    theme: str = "default"
    supports_dark_mode: bool = True
    
    plotly_json: Dict[str, Any]
