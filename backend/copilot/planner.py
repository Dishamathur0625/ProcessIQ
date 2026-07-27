import json
from typing import List, Dict, Any
from backend.orchestrator.capability_registry import CAPABILITY_REGISTRY

class AIPlanner:
    """
    The Planner Agent.
    Receives user natural language requests and maps them to supported capabilities.
    Extracts intents and parameters as structured JSON.
    """
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        
    def build_prompt(self, user_request: str) -> str:
        supported_ops = list(CAPABILITY_REGISTRY.keys())
        prompt = f"""
You are the ProcessIQ Workflow Planner. 
Your job is to translate the user's natural language request into a structured JSON execution plan.
You MUST ONLY use operations from the following supported list:
{supported_ops}

User Request: "{user_request}"

Output Format:
{{
    "plan": [
        {{"operation": "operation_name", "column": "column_name"}}
    ]
}}
"""
        return prompt
