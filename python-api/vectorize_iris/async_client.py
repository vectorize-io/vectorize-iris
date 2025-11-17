"""
Asynchronous client for Vectorize Iris text extraction
"""

import os
import asyncio
import aiohttp
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


async def _extract_from_bytes_async(
    file_content: bytes,
    file_name: str,
    api_token: str,
    org_id: str,
    poll_interval: int,
    timeout: int,
    options: Optional[ExtractionOptions] = None
) -> ExtractionResultData:
    """
    Internal async function to extract from file bytes.
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

    async with aiohttp.ClientSession() as session:
        # Step 1: Start file upload and get presigned URL
        upload_request = StartFileUploadRequest(
            name=file_name,
            content_type="application/octet-stream"
        )

        async with session.post(
            f"{base_url}/files",
            headers=headers,
            json=upload_request.model_dump(by_alias=True)
        ) as upload_response:
            if upload_response.status != 200:
                error_text = await upload_response.text()
                raise VectorizeIrisError(
                    f"Failed to start upload: {upload_response.status} - {error_text}"
                )

            upload_data = StartFileUploadResponse(**(await upload_response.json()))

        # Step 2: Upload file to presigned URL
        upload_headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(file_size)
        }

        async with session.put(
            upload_data.upload_url,
            data=file_content,
            headers=upload_headers
        ) as put_response:
            if put_response.status not in (200, 201, 204):
                error_text = await put_response.text()
                raise VectorizeIrisError(
                    f"Failed to upload file: {put_response.status} - {error_text}"
                )

        # Step 3: Start extraction
        extraction_request = options.to_extraction_request(upload_data.file_id)

        async with session.post(
            f"{base_url}/extraction",
            headers=headers,
            json=extraction_request.model_dump(by_alias=True, exclude_none=True)
        ) as extraction_response:
            if extraction_response.status != 200:
                error_text = await extraction_response.text()
                raise VectorizeIrisError(
                    f"Failed to start extraction: {extraction_response.status} - {error_text}"
                )

            extraction_data = StartExtractionResponse(**(await extraction_response.json()))

        # Step 4: Poll for completion
        start_time = asyncio.get_event_loop().time()

        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise VectorizeIrisError(f"Extraction timed out after {timeout} seconds")

            async with session.get(
                f"{base_url}/extraction/{extraction_data.extraction_id}",
                headers=headers
            ) as status_response:
                if status_response.status != 200:
                    error_text = await status_response.text()
                    raise VectorizeIrisError(
                        f"Failed to check status: {status_response.status} - {error_text}"
                    )

                result = ExtractionResult(**(await status_response.json()))

                if result.ready:
                    if result.data is None:
                        raise VectorizeIrisError("Extraction completed but no data was returned")

                    if not result.data.success:
                        error_msg = result.data.error or "Unknown error"
                        raise VectorizeIrisError(f"Extraction failed: {error_msg}")

                    return result.data

            # Still processing, wait and retry
            await asyncio.sleep(poll_interval)


async def extract_text_async(
    file_bytes: bytes,
    file_name: str = "document.pdf",
    api_token: Optional[str] = None,
    org_id: Optional[str] = None,
    poll_interval: int = 2,
    timeout: int = 300,
    options: Optional[ExtractionOptions] = None
) -> ExtractionResultData:
    """
    Extract text from file bytes using Vectorize Iris (asynchronous).

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
    """
    # Get credentials from environment if not provided
    api_token = api_token or os.getenv('VECTORIZE_API_TOKEN')
    org_id = org_id or os.getenv('VECTORIZE_ORG_ID')

    if not api_token or not org_id:
        raise VectorizeIrisError(
            "Missing credentials. Set VECTORIZE_API_TOKEN and VECTORIZE_ORG_ID "
            "environment variables or pass them as parameters."
        )

    return await _extract_from_bytes_async(
        file_bytes, file_name, api_token, org_id, poll_interval, timeout, options
    )


async def extract_text_from_file_async(
    file_path: str,
    api_token: Optional[str] = None,
    org_id: Optional[str] = None,
    poll_interval: int = 2,
    timeout: int = 300,
    options: Optional[ExtractionOptions] = None
) -> ExtractionResultData:
    """
    Extract text from a file using Vectorize Iris (asynchronous).

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

    return await _extract_from_bytes_async(
        file_content, file_name, api_token, org_id, poll_interval, timeout, options
    )
