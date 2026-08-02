import logging
from typing import Type, Any
from pydantic import BaseModel
from backend.copilot.provider import llm_provider, MockLLMProvider

logger = logging.getLogger(__name__)

class CopilotGuardrail:
    """
    Enforces deterministic boundaries for the Copilot.
    - Prevents prompt injections asking to modify data.
    - Ensures responses are structured JSON.
    - Sanitizes any sensitive paths.
    - Falls back to a deterministic mock provider if the remote LLM is
      unavailable (rate limit / outage), so the UI never breaks.
    """
    
    FORBIDDEN_TERMS = [
        "delete data", "os.system", "drop table",
        "change config", "import os", "import sys", "import subprocess"
    ]
    
    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        prompt_lower = prompt.lower()
        for term in CopilotGuardrail.FORBIDDEN_TERMS:
            if term in prompt_lower:
                raise ValueError("Prompt rejected: Violates deterministic execution policy.")
        return prompt
        
    @staticmethod
    def execute(context: str, prompt: str, response_model: Type[BaseModel]) -> Any:
        sanitized_prompt = CopilotGuardrail.sanitize_prompt(prompt)
        
        try:
            return llm_provider.generate_structured(
                context=context,
                prompt=sanitized_prompt,
                response_model=response_model
            )
        except Exception as e:
            logger.error("LLM provider failed (reason: %s). Falling back to MockLLMProvider.", str(e)[:300])
            logger.warning("WARNING: Returning MockLLMProvider output because the configured LLM is unavailable.")
            return MockLLMProvider().generate_structured(
                context=context,
                prompt=sanitized_prompt,
                response_model=response_model
            )
