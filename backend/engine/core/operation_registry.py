from typing import Dict, Type, Any, List
from .exceptions import UnsupportedOperationError
from .metadata import OperationMetadata

class OperationRegistry:
    """
    Dynamic registry for all preprocessing operations.
    Allows LLMs and the UI to discover capabilities programmatically.
    """
    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, operation_class: Type, metadata: OperationMetadata):
        cls._registry[metadata.name] = {
            "class": operation_class,
            "metadata": metadata
        }

    @classmethod
    def get_metadata(cls, name: str) -> OperationMetadata:
        if name not in cls._registry:
            raise UnsupportedOperationError(f"Operation '{name}' not found.")
        return cls._registry[name]["metadata"]
        
    @classmethod
    def get_class(cls, name: str) -> Type:
        if name not in cls._registry:
            raise UnsupportedOperationError(f"Operation '{name}' not found.")
        return cls._registry[name]["class"]

    @classmethod
    def list_all(cls) -> List[Dict[str, Any]]:
        return [
            {"name": name, "metadata": data["metadata"].model_dump()}
            for name, data in cls._registry.items()
        ]
