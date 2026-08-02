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

class InteractiveTransformRequest(BaseModel):
    job_id: str
    user_intent: str
    dataset_path: Optional[str] = None
    output_path: Optional[str] = None

class InteractiveTransformLLMResponse(BaseModel):
    python_code: str = Field(description="The executable python pandas code to transform the dataset")
    explanation: str = Field(description="Explanation of what the code does")
    success: bool = Field(default=True, description="Whether the code generation was successful")

class InteractiveTransformResponse(BaseModel):
    python_code: str = Field(description="The executable python pandas code to transform the dataset")
    explanation: str = Field(description="Explanation of what the code does")
    success: bool = Field(default=True, description="Whether the code generation was successful")
    updated_stats: Optional[Dict[str, Any]] = Field(default=None, description="Updated dataset statistics after transformation")
    before_stats: Optional[Dict[str, Any]] = Field(default=None, description="EDA statistics of the dataset before transformation")
    output_file: Optional[str] = Field(default=None, description="Storage path of the generated output file")
    download_url: Optional[str] = Field(default=None, description="URL to download the generated output file")
    preview_data: Optional[List[Dict[str, Any]]] = Field(default=None, description="Preview of the first few rows of the transformed dataset")

class EDAStatsResponse(BaseModel):
    job_id: str = Field(description="The job/dataset id the statistics belong to")
    overview: Dict[str, Any] = Field(description="Dataset-level summary (rows, columns, duplicates, missing cells, ...)")
    columns: Dict[str, Any] = Field(description="Per-column statistics: mean, median, mode, std, min, max, nulls, unique, ...")
    source: str = Field(description="Which file the statistics were computed from")
    generated_at: str = Field(description="ISO timestamp of generation")

class EDAAssistantResponse(BaseModel):
    question: str = Field(description="A clarifying question the Copilot asks the user about what they want to do with the dataset")
    suggestions: List[str] = Field(description="Example intents the user could type next")
    context_summary: str = Field(description="Short summary of what the EDA already revealed about the dataset")
    references: List[str] = Field(description="Artifacts used to build this response")
