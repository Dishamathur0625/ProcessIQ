from typing import Dict, Type, Any, Optional

class ProcessIQError(Exception):
    """Base exception for all ProcessIQ errors."""
    pass

class DataLeakageError(ProcessIQError):
    """Raised when an operation detects potential data leakage (e.g. scaling with target)."""
    pass

class EmptyDatasetError(ProcessIQError):
    """Raised when an operation is applied to an empty dataframe."""
    pass

class TypeMismatchError(ProcessIQError):
    """Raised when an operation is applied to an incompatible column type."""
    pass

class UnsupportedOperationError(ProcessIQError):
    """Raised when an unregistered operation is requested."""
    pass
