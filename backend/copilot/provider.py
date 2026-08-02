import json
import logging
from abc import ABC, abstractmethod
from typing import Type, Any
from pydantic import BaseModel
import openai
from google import genai

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Placeholder / obviously-invalid keys that should fall back to the mock provider
_PLACEHOLDER_KEYS = {
    "yAQ.Ab8RN6LTidWx7F1uAa2l1XNn7G0xPO18vzUuoWH9NastQMsA7w",
    "your-gemini-api-key",
    "",
}

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_structured(self, context: str, prompt: str, response_model: Type[BaseModel], model: str = None) -> Any:
        pass

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.default_model = settings.OPENAI_MODEL
        
    def generate_structured(self, context: str, prompt: str, response_model: Type[BaseModel], model: str = None) -> Any:
        target_model = model or self.default_model
        system_message = (
            "You are the Intelligent Copilot for ProcessIQ. "
            "You must strictly interpret the provided context and provide insights.\n"
            f"Context:\n{context}"
        )
        try:
            response = self.client.beta.chat.completions.parse(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                response_format=response_model,
                temperature=0.0
            )
            return response.choices[0].message.parsed
        except Exception as e:
            raise RuntimeError(f"OpenAI Generation failed: {str(e)}")

class GeminiProvider(BaseLLMProvider):
    # Ordered fallback models: newer/preferred first. `gemini-flash-latest` is an alias
    # that is stable, whereas pinned versions get decommissioned for new projects.
    FALLBACK_MODELS = [
        "gemini-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.default_model = settings.GEMINI_MODEL
        self._working_model = None

    def _candidates(self, requested: str):
        seen = []
        for m in [requested, self.default_model] + self.FALLBACK_MODELS:
            if m and m not in seen:
                seen.append(m)
        return seen

    def generate_structured(self, context: str, prompt: str, response_model: Type[BaseModel], model: str = None) -> Any:
        system_instruction = (
            "You are the Intelligent Copilot for ProcessIQ, an enterprise data analytics engine. "
            "You must interpret the provided deterministic context and provide insights. "
            "You must NOT hallucinate information not present in the context. "
            "You must NOT suggest executing arbitrary code or non-deterministic transformations. "
            f"\n\nContext:\n{context}"
        )

        last_error = None
        candidates = self._candidates(model or self.default_model)

        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

        def _call(target_model: str):
            return self.client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_model,
                    system_instruction=system_instruction,
                    temperature=0.0,
                ),
            )

        for candidate in candidates:
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(_call, candidate)
                    response = future.result(timeout=45)
                self._working_model = candidate
                return response_model.model_validate_json(response.text)
            except FutureTimeout:
                last_error = RuntimeError(f"Gemini model {candidate} timed out after 45s.")
                logger.warning(str(last_error))
                continue
            except Exception as e:
                last_error = e
                logger.warning("Gemini generation failed with model %s: %s", candidate, str(e)[:300])
                continue

        raise RuntimeError(f"Gemini Generation failed for all candidate models: {last_error}")

class MockLLMProvider(BaseLLMProvider):
    def generate_structured(self, context: str, prompt: str, response_model: Type[BaseModel], model: str = None) -> Any:
        import time
        time.sleep(1) # Simulate network delay
        
        # Determine which response model is being requested and return a mock
        model_name = response_model.__name__
        
        if model_name == "InteractiveTransformLLMResponse":
            return response_model(
                python_code="numeric_cols = df.select_dtypes(include='number').columns\nfor col in numeric_cols:\n    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(df[col].median())",
                explanation="I have imputed all missing numeric values with their respective medians.",
                success=True
            )
        elif model_name == "EDAAssistantResponse":
            return response_model(
                question="What would you like me to do with this dataset next?",
                suggestions=[
                    "Impute missing values with the median",
                    "Drop rows with too many missing values",
                    "Pivot plant data based on the variable column",
                ],
                context_summary="The dataset appears to contain a mix of numeric and categorical columns (fallback summary because the configured LLM is unavailable).",
                references=["eda_stats"]
            )
        elif model_name == "DatasetUnderstandingResponse":
            return response_model(
                title="Mock Dataset Analysis",
                summary="This is a mock summary because the API key is invalid.",
                recommendations=["Impute missing values", "Remove outliers"],
                confidence=0.9,
                references=["dataset_profile"]
            )
        elif model_name == "PipelineSuggestionResponse":
            return response_model(
                name="Mock Pipeline",
                steps={"validation": True, "cleaning": True, "feature_engineering": False, "feature_selection": False, "visualization": True, "reports": True},
                reasoning=["Mock reasoning for cleaning", "Mock reasoning for validation"]
            )
        else:
            raise ValueError(f"Mock provider does not support {model_name}")

class ProviderFactory:
    @staticmethod
    def get_provider() -> BaseLLMProvider:
        provider_name = settings.LLM_PROVIDER.lower()
        
        # If using gemini but the key is missing/placeholder, fallback to mock provider
        if provider_name == "gemini" and settings.GEMINI_API_KEY in _PLACEHOLDER_KEYS:
            print("WARNING: Using MockLLMProvider because a valid Gemini API key was not found.")
            return MockLLMProvider()
            
        if provider_name == "gemini":
            return GeminiProvider()
        elif provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "mock":
            return MockLLMProvider()
        else:
            raise ValueError(f"Unknown LLM Provider: {provider_name}")

# Singleton instance for backward compatibility with guardrail.py
llm_provider = ProviderFactory.get_provider()
