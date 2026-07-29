from fastapi import APIRouter, Depends, HTTPException
import logging

from backend.schemas.copilot import (
    CopilotRequest,
    DatasetUnderstandingResponse,
    PipelineSuggestionResponse,
    ChartExplanationResponse,
    ReportExplanationResponse,
    ChatResponse
)
from backend.copilot.context_builder import ContextBuilder
from backend.copilot.guardrail import CopilotGuardrail
from backend.copilot.prompts import PromptLibrary

router = APIRouter(tags=["Copilot"])
logger = logging.getLogger(__name__)

@router.post("/dataset-understanding", response_model=DatasetUnderstandingResponse)
def understand_dataset(request: CopilotRequest):
    logger.info(f"Copilot: Dataset Understanding for job {request.job_id}")
    context = ContextBuilder.build_context(request.job_id, ["dataset_profile"])
    prompt = request.question or PromptLibrary.DATASET_OVERVIEW
    
    return CopilotGuardrail.execute(
        context=context,
        prompt=prompt,
        response_model=DatasetUnderstandingResponse
    )

@router.post("/pipeline-suggestion", response_model=PipelineSuggestionResponse)
def suggest_pipeline(request: CopilotRequest):
    logger.info(f"Copilot: Pipeline Suggestion for job {request.job_id}")
    context = ContextBuilder.build_context(request.job_id, ["dataset_profile", "quality_report"])
    prompt = PromptLibrary.PIPELINE_RECOMMENDATION
    
    return CopilotGuardrail.execute(
        context=context,
        prompt=prompt,
        response_model=PipelineSuggestionResponse
    )

@router.post("/explain-chart", response_model=ChartExplanationResponse)
def explain_chart(request: CopilotRequest):
    logger.info(f"Copilot: Explain Chart for job {request.job_id}")
    context = ContextBuilder.build_context(request.job_id, ["visualizations"])
    prompt = request.question or PromptLibrary.EXPLAIN_CHART
    
    return CopilotGuardrail.execute(
        context=context,
        prompt=prompt,
        response_model=ChartExplanationResponse
    )

@router.post("/explain-report", response_model=ReportExplanationResponse)
def explain_report(request: CopilotRequest):
    logger.info(f"Copilot: Explain Report for job {request.job_id}")
    context = ContextBuilder.build_context(request.job_id, ["reports", "quality_report"])
    prompt = request.question or PromptLibrary.EXPLAIN_REPORT
    
    return CopilotGuardrail.execute(
        context=context,
        prompt=prompt,
        response_model=ReportExplanationResponse
    )

@router.post("/chat", response_model=ChatResponse)
def chat(request: CopilotRequest):
    logger.info(f"Copilot: Chat for job {request.job_id} - {request.question}")
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required for chat endpoint.")
        
    # By default, load everything for a chat, or use specific context keys if provided
    context = ContextBuilder.build_context(request.job_id, request.context_keys)
    
    return CopilotGuardrail.execute(
        context=context,
        prompt=request.question,
        response_model=ChatResponse
    )
