"""
Vectorize Iris - Simple Text Extraction API
Extract text from files using Vectorize Iris with a single function call.
"""

from vectorize_iris.exceptions import VectorizeIrisError
from vectorize_iris.client import extract_text, extract_text_from_file
from vectorize_iris.async_client import extract_text_async, extract_text_from_file_async
from vectorize_iris.models import (
    ExtractionOptions,
    ExtractionResultData,
    MetadataExtractionStrategySchema,
    MetadataExtractionStrategy,
)

__all__ = [
    # Exceptions
    "VectorizeIrisError",
    # Sync functions
    "extract_text",
    "extract_text_from_file",
    # Async functions
    "extract_text_async",
    "extract_text_from_file_async",
    # Models
    "ExtractionOptions",
    "ExtractionResultData",
    "MetadataExtractionStrategySchema",
    "MetadataExtractionStrategy",
]

__version__ = "0.1.0"
