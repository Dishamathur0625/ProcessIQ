from fastapi import APIRouter, Depends, HTTPException
import logging
from datetime import datetime

from backend.schemas.copilot import (
    CopilotRequest,
    DatasetUnderstandingResponse,
    PipelineSuggestionResponse,
    ChartExplanationResponse,
    ReportExplanationResponse,
    ChatResponse,
    InteractiveTransformRequest,
    InteractiveTransformResponse,
    EDAStatsResponse,
    EDAAssistantResponse,
)
from backend.copilot.context_builder import ContextBuilder
from backend.copilot.guardrail import CopilotGuardrail
from backend.copilot.prompts import PromptLibrary
from backend.copilot.code_executor import CodeExecutor
from backend.copilot.dataset_loader import load_job_dataframe, save_job_dataframe
from backend.engine.profiling.eda_stats import compute_eda_stats

router = APIRouter(tags=["Copilot"])
logger = logging.getLogger(__name__)


def _job_eda_context(job_id: str) -> str:
    """Build a compact markdown block containing the deterministic EDA statistics."""
    import json
    try:
        df = load_job_dataframe(job_id)
        eda = compute_eda_stats(df)
        return "### EDA Statistics (computed with pandas)\n```json\n" + json.dumps(
            eda, default=str
        ) + "\n```"
    except Exception as e:
        logger.warning("Could not compute EDA for job %s: %s", job_id, e)
        return "### EDA Statistics\n(EDA statistics could not be computed for this job yet.)"


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


@router.post("/eda-stats", response_model=EDAStatsResponse)
def get_eda_stats(request: CopilotRequest):
    """
    Runs deterministic pandas EDA on the uploaded dataset and returns the
    statistics (mean, median, mode, std, quantiles, skew, missing values, ...).
    These same values are shown in the dashboard and given to the LLM as context.
    """
    logger.info(f"Copilot: EDA stats for job {request.job_id}")
    df = load_job_dataframe(request.job_id)
    eda = compute_eda_stats(df)

    # Persist as an artifact so the dashboard / reports can reference it later.
    try:
        import json as _json
        from backend.services.storage.factory import StorageFactory
        import io
        storage = StorageFactory.get_backend()
        storage.upload(
            "artifacts",
            f"{request.job_id}/eda_report.json",
            io.BytesIO(_json.dumps(eda, default=str).encode("utf-8")),
        )
    except Exception as e:
        logger.warning("Failed to persist EDA artifact for %s: %s", request.job_id, e)

    return EDAStatsResponse(
        job_id=request.job_id,
        overview=eda["overview"],
        columns=eda["columns"],
        source=f"{request.job_id}/dataset.csv",
        generated_at=datetime.utcnow().isoformat() + "Z",
    )


@router.post("/eda-assistant", response_model=EDAAssistantResponse)
def eda_assistant(request: CopilotRequest):
    """
    Starts the interactive EDA conversation: the LLM greets the user, summarizes
    what the deterministic stats reveal, and asks what they would like to do next.
    """
    logger.info(f"Copilot: EDA assistant opener for job {request.job_id}")
    context = _job_eda_context(request.job_id)
    
    return CopilotGuardrail.execute(
        context=context,
        prompt=PromptLibrary.EDA_ASSISTANT,
        response_model=EDAAssistantResponse
    )


@router.post("/interactive-transform", response_model=InteractiveTransformResponse)
def interactive_transform(request: InteractiveTransformRequest):
    logger.info(f"Copilot: Interactive Transform for job {request.job_id}")
    
    from backend.schemas.copilot import InteractiveTransformLLMResponse
    from backend.core.config import settings
    from backend.services.storage.factory import StorageFactory
    storage = StorageFactory.get_backend()

    dataset_path = request.dataset_path or f"copilot/{request.job_id}/interactive.csv"
    if storage.exists(settings.SUPABASE_BUCKET_PROCESSED, dataset_path):
        bucket = settings.SUPABASE_BUCKET_PROCESSED
    else:
        dataset_path = f"{request.job_id}/dataset.csv"
        bucket = settings.SUPABASE_BUCKET_DATASETS

    # Load the dataset directly from storage and compute the before-state EDA.
    df = load_job_dataframe(request.job_id, bucket=bucket, path=dataset_path)
    before_stats = compute_eda_stats(df)
    
    import json
    eda_context = (
        "### Current Dataset EDA Statistics (computed with pandas)\n```json\n"
        + json.dumps(before_stats, default=str)
        + "\n```\n\n"
    )
    static_context = ContextBuilder.build_context(request.job_id, ["dataset_profile", "feature_metadata"])
    context = eda_context + static_context
    
    try:
        llm_response: InteractiveTransformLLMResponse = CopilotGuardrail.execute(
            context=context,
            prompt=f"{PromptLibrary.INTERACTIVE_TRANSFORM}\n\nUser Intent: {request.user_intent}",
            response_model=InteractiveTransformLLMResponse
        )
        
        updated_stats = None
        output_file = None
        download_url = None
        
        if llm_response.success and llm_response.python_code:
            logger.info("Executing generated python code on dataset.")
            
            # Execute the generated pandas code against the in-memory dataframe.
            modified_df = CodeExecutor.execute_on_df(llm_response.python_code, df)
            
            # Persist the transformed dataset as the processed output file.
            output_file = save_job_dataframe(
                request.job_id, modified_df,
                path=request.output_path or f"copilot/{request.job_id}/interactive.csv",
            )
            download_url = f"/api/v1/download/{request.job_id}"
            
            # Recompute full EDA statistics (mean, median, mode, std, ...) after the change.
            import pandas as pd
            updated_stats = {}
            for col in modified_df.columns:
                if pd.api.types.is_numeric_dtype(modified_df[col]):
                    updated_stats[col] = {
                        "mean": modified_df[col].mean() if not pd.isna(modified_df[col].mean()) else None,
                        "median": modified_df[col].median() if not pd.isna(modified_df[col].median()) else None,
                        "mode": modified_df[col].mode()[0] if not modified_df[col].mode().empty else None,
                        "std": modified_df[col].std() if not pd.isna(modified_df[col].std()) else None,
                        "min": modified_df[col].min() if not pd.isna(modified_df[col].min()) else None,
                        "max": modified_df[col].max() if not pd.isna(modified_df[col].max()) else None,
                        "nulls": int(modified_df[col].isnull().sum())
                    }
                else:
                    updated_stats[col] = {
                        "mode": modified_df[col].mode()[0] if not modified_df[col].mode().empty else None,
                        "unique": modified_df[col].nunique(),
                        "nulls": int(modified_df[col].isnull().sum())
                    }
        
        return InteractiveTransformResponse(
            python_code=llm_response.python_code,
            explanation=llm_response.explanation,
            success=llm_response.success,
            updated_stats=updated_stats,
            before_stats=before_stats["columns"],
            output_file=output_file,
            download_url=download_url,
            preview_data=modified_df.head(5).fillna("").to_dict(orient="records") if updated_stats else None
        )
    except Exception as e:
        logger.error(f"Error in interactive_transform: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
