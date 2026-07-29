from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DatasetUnderstandingResponse(BaseModel):
    title: str = Field(description="Title of the insight")
    summary: str = Field(description="A concise summary of the dataset characteristics and likely ML task")
    recommendations: List[str] = Field(description="List of recommended preprocessing steps based on the profile")
    confidence: float = Field(description="Confidence score between 0 and 1")
    references: List[str] = Field(description="List of artifacts referenced (e.g. 'Dataset Profile')")

class PipelineSuggestionResponse(BaseModel):
    name: str = Field(description="Name of the suggested pipeline")
    steps: Dict[str, bool] = Field(description="A dictionary mapping pipeline stages to boolean execution flags")
    reasoning: List[str] = Field(description="List of reasons for suggesting these steps based on the dataset profile")

class ChartExplanationResponse(BaseModel):
    finding: str = Field(description="Key finding from the chart")
    evidence: str = Field(description="Statistical evidence supporting the finding")
    impact: str = Field(description="Potential impact on ML models")
    recommendation: str = Field(description="Actionable recommendation based on the finding")

class ReportExplanationResponse(BaseModel):
    summary: str = Field(description="High-level summary of the pipeline's impact on data quality")
    improvements: List[str] = Field(description="List of key improvements achieved")
    remaining_concerns: List[str] = Field(description="List of any remaining issues or warnings")

class ChatResponse(BaseModel):
    answer: str = Field(description="The response to the user's question")
    recommendation: Optional[str] = Field(default=None, description="Actionable recommendation if applicable")
    references: List[str] = Field(description="List of artifacts or metadata fields referenced")

class CopilotRequest(BaseModel):
    job_id: str
    prompt_id: Optional[str] = None
    question: Optional[str] = None
    context_keys: Optional[List[str]] = None
