import json
from abc import ABC, abstractmethod
from typing import Type, Any
from pydantic import BaseModel
import openai
from google import genai

from backend.core.config import settings

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
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.default_model = settings.GEMINI_MODEL

    def generate_structured(self, context: str, prompt: str, response_model: Type[BaseModel], model: str = None) -> Any:
        target_model = model or self.default_model
        system_instruction = (
            "You are the Intelligent Copilot for ProcessIQ, an enterprise data analytics engine. "
            "You must interpret the provided deterministic context and provide insights. "
            "You must NOT hallucinate information not present in the context. "
            "You must NOT suggest executing arbitrary code or non-deterministic transformations. "
            f"\n\nContext:\n{context}"
        )
        try:
            response = self.client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_model,
                    system_instruction=system_instruction,
                    temperature=0.0,
                ),
            )
            return response_model.model_validate_json(response.text)
        except Exception as e:
            raise RuntimeError(f"Gemini Generation failed: {str(e)}")

class ProviderFactory:
    @staticmethod
    def get_provider() -> BaseLLMProvider:
        provider_name = settings.LLM_PROVIDER.lower()
        if provider_name == "gemini":
            return GeminiProvider()
        elif provider_name == "openai":
            return OpenAIProvider()
        else:
            raise ValueError(f"Unknown LLM Provider: {provider_name}")

# Singleton instance for backward compatibility with guardrail.py
llm_provider = ProviderFactory.get_provider()
