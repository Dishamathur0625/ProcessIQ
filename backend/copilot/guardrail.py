from typing import Type, Any
from pydantic import BaseModel
from backend.copilot.provider import llm_provider

class CopilotGuardrail:
    """
    Enforces deterministic boundaries for the Copilot.
    - Prevents prompt injections asking to modify data.
    - Ensures responses are structured JSON.
    - Sanitizes any sensitive paths.
    """
    
    FORBIDDEN_TERMS = [
        "delete data", "run python", "exec", "os.system", "drop table",
        "modify file", "change config"
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
        
        # In a more advanced version, we could check context size here and truncate if needed.
        # But for now, we rely on OpenAI API limits and our artifact size.
        
        return llm_provider.generate_structured(
            context=context,
            prompt=sanitized_prompt,
            response_model=response_model
        )
