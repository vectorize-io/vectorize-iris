"""
Synchronous client for Vectorize Iris text extraction
"""

import os
import time
import requests
from typing import Optional
from pathlib import Path

from vectorize_iris.exceptions import VectorizeIrisError
from vectorize_iris.models import (
    StartFileUploadRequest,
    StartFileUploadResponse,
    StartExtractionRequest,
    StartExtractionResponse,
    ExtractionResult,
    ExtractionResultData,
    ExtractionOptions,
)


def _extract_from_bytes(
    file_content: bytes,
    file_name: str,
    api_token: str,
    org_id: str,
    poll_interval: int,
    timeout: int,
    options: Optional[ExtractionOptions] = None
) -> ExtractionResultData:
    """
    Internal function to extract from file bytes.
    """
    base_url = f"https://api.vectorize.io/v1/org/{org_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    file_size = len(file_content)

    # Default options if not provided
    if options is None:
        options = ExtractionOptions()

    # Step 1: Start file upload and get presigned URL
    upload_request = StartFileUploadRequest(
        name=file_name,
        content_type="application/octet-stream"
    )

    upload_response = requests.post(
        f"{base_url}/files",
        headers=headers,
        json=upload_request.model_dump(by_alias=True)
    )

    if upload_response.status_code != 200:
        raise VectorizeIrisError(
            f"Failed to start upload: {upload_response.status_code} - {upload_response.text}"
        )

    upload_data = StartFileUploadResponse(**upload_response.json())

    # Step 2: Upload file to presigned URL
    upload_headers = {
        "Content-Type": "application/octet-stream",
        "Content-Length": str(file_size)
    }

    put_response = requests.put(upload_data.upload_url, data=file_content, headers=upload_headers)

    if put_response.status_code not in (200, 201, 204):
        raise VectorizeIrisError(
            f"Failed to upload file: {put_response.status_code} - {put_response.text}"
        )

    # Step 3: Start extraction
    extraction_request = options.to_extraction_request(upload_data.file_id)

    extraction_response = requests.post(
        f"{base_url}/extraction",
        headers=headers,
        json=extraction_request.model_dump(by_alias=True, exclude_none=True)
    )

    if extraction_response.status_code != 200:
        raise VectorizeIrisError(
            f"Failed to start extraction: {extraction_response.status_code} - {extraction_response.text}"
        )

    extraction_data = StartExtractionResponse(**extraction_response.json())

    # Step 4: Poll for completion
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            raise VectorizeIrisError(f"Extraction timed out after {timeout} seconds")

        status_response = requests.get(
            f"{base_url}/extraction/{extraction_data.extraction_id}",
            headers=headers
        )

        if status_response.status_code != 200:
            raise VectorizeIrisError(
                f"Failed to check status: {status_response.status_code} - {status_response.text}"
            )

        result = ExtractionResult(**status_response.json())

        if result.ready:
            if result.data is None:
                raise VectorizeIrisError("Extraction completed but no data was returned")

            if not result.data.success:
                error_msg = result.data.error or "Unknown error"
                raise VectorizeIrisError(f"Extraction failed: {error_msg}")

            return result.data

        # Still processing, wait and retry
        time.sleep(poll_interval)


def extract_text(
    file_bytes: bytes,
    file_name: str = "document.pdf",
    api_token: Optional[str] = None,
    org_id: Optional[str] = None,
    poll_interval: int = 2,
    timeout: int = 300,
    options: Optional[ExtractionOptions] = None
) -> ExtractionResultData:
    """
    Extract text from file bytes using Vectorize Iris (synchronous).

    Args:
        file_bytes: File content as bytes
        file_name: Name of the file (default: "document.pdf")
        api_token: Vectorize API token (defaults to VECTORIZE_API_TOKEN env var)
        org_id: Organization ID (defaults to VECTORIZE_ORG_ID env var)
        poll_interval: Seconds to wait between status checks (default: 2)
        timeout: Maximum seconds to wait for extraction (default: 300)
        options: Extraction options (chunking, metadata, etc.)

    Returns:
        ExtractionResultData containing text, chunks, metadata, etc.

    Raises:
        VectorizeIrisError: If extraction fails or times out

    Example:
        >>> with open("document.pdf", "rb") as f:
        ...     file_bytes = f.read()
        >>> result = extract_text(file_bytes, "document.pdf")
        >>> print(result.text)
        >>> print(result.chunks)  # If chunking was requested
    """
    # Get credentials from environment if not provided
    api_token = api_token or os.getenv('VECTORIZE_API_TOKEN')
    org_id = org_id or os.getenv('VECTORIZE_ORG_ID')

    if not api_token or not org_id:
        raise VectorizeIrisError(
            "Missing credentials. Set VECTORIZE_API_TOKEN and VECTORIZE_ORG_ID "
            "environment variables or pass them as parameters."
        )

    return _extract_from_bytes(
        file_bytes, file_name, api_token, org_id, poll_interval, timeout, options
    )


def extract_text_from_file(
    file_path: str,
    api_token: Optional[str] = None,
    org_id: Optional[str] = None,
    poll_interval: int = 2,
    timeout: int = 300,
    options: Optional[ExtractionOptions] = None
) -> ExtractionResultData:
    """
    Extract text from a file using Vectorize Iris (synchronous).

    Args:
        file_path: Path to the file to extract text from
        api_token: Vectorize API token (defaults to VECTORIZE_API_TOKEN env var)
        org_id: Organization ID (defaults to VECTORIZE_ORG_ID env var)
        poll_interval: Seconds to wait between status checks (default: 2)
        timeout: Maximum seconds to wait for extraction (default: 300)
        options: Extraction options (chunking, metadata, etc.)

    Returns:
        ExtractionResultData containing text, chunks, metadata, etc.

    Raises:
        VectorizeIrisError: If extraction fails or times out
        FileNotFoundError: If the file doesn't exist

    Example:
        >>> from vectorize_iris.models import ExtractionOptions, MetadataExtractionStrategySchema
        >>>
        >>> # Simple extraction (text only)
        >>> result = extract_text_from_file("document.pdf")
        >>> print(result.text)
        >>>
        >>> # With chunking
        >>> options = ExtractionOptions(
        ...     chunking_strategy="markdown",
        ...     chunk_size=512
        ... )
        >>> result = extract_text_from_file("document.pdf", options=options)
        >>> for chunk in result.chunks:
        ...     print(chunk)
        >>>
        >>> # With metadata extraction
        >>> options = ExtractionOptions(
        ...     metadata_schemas=[
        ...         MetadataExtractionStrategySchema(
        ...             id="doc-meta",
        ...             schema_="Extract: title, author, date"
        ...         )
        ...     ]
        ... )
        >>> result = extract_text_from_file("document.pdf", options=options)
        >>> print(result.metadata)  # JSON string
    """
    # Get credentials from environment if not provided
    api_token = api_token or os.getenv('VECTORIZE_API_TOKEN')
    org_id = org_id or os.getenv('VECTORIZE_ORG_ID')

    if not api_token or not org_id:
        raise VectorizeIrisError(
            "Missing credentials. Set VECTORIZE_API_TOKEN and VECTORIZE_ORG_ID "
            "environment variables or pass them as parameters."
        )

    # Validate file exists and read content
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'rb') as f:
        file_content = f.read()

    file_name = file_path_obj.name

    return _extract_from_bytes(
        file_content, file_name, api_token, org_id, poll_interval, timeout, options
    )
