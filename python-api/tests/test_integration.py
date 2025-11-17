"""
Integration tests for Vectorize Iris Python API
These tests require real API credentials and network access
"""

import os
import pytest
from pathlib import Path
from vectorize_iris import (
    extract_text,
    extract_text_from_file,
    extract_text_async,
    extract_text_from_file_async,
    VectorizeIrisError,
    ExtractionOptions,
    MetadataExtractionStrategySchema,
)


# Skip all tests if credentials are not available
pytestmark = pytest.mark.skipif(
    not os.getenv("VECTORIZE_API_TOKEN") or not os.getenv("VECTORIZE_ORG_ID"),
    reason="API credentials not found"
)


def get_test_file() -> Path:
    """Get path to test file"""
    return Path(__file__).parent.parent.parent / "examples" / "sample.md"


class TestSyncIntegration:
    """Integration tests for sync client"""

    def test_extract_text_from_file_simple(self):
        """Test simple extraction from file"""
        result = extract_text_from_file(str(get_test_file()))

        assert result.success is True
        assert result.text is not None
        assert len(result.text) > 0
        print(f"\n✓ Extracted {len(result.text)} characters")

    def test_extract_text_from_bytes(self):
        """Test extraction from bytes"""
        test_file = get_test_file()
        with open(test_file, "rb") as f:
            file_bytes = f.read()

        result = extract_text(
            file_bytes=file_bytes,
            file_name=test_file.name
        )

        assert result.success is True
        assert result.text is not None
        assert len(result.text) > 0

    def test_extract_with_chunking(self):
        """Test extraction with chunking"""
        options = ExtractionOptions(
            chunk_size=512
        )

        result = extract_text_from_file(
            str(get_test_file()),
            options=options
        )

        assert result.success is True
        assert result.chunks is not None
        assert len(result.chunks) > 0
        print(f"\n✓ Generated {len(result.chunks)} chunks")

    def test_extract_with_metadata(self):
        """Test extraction with metadata schemas"""
        # Skip this test for now - metadata extraction has API issues
        pytest.skip("Metadata extraction has backend parsing issues")

    def test_extract_with_infer_metadata(self):
        """Test extraction with inferred metadata schema"""
        options = ExtractionOptions(
            infer_metadata_schema=True
        )

        result = extract_text_from_file(
            str(get_test_file()),
            options=options
        )

        assert result.success is True

    def test_extract_with_parsing_instructions(self):
        """Test extraction with parsing instructions"""
        options = ExtractionOptions(
            parsing_instructions="Focus on extracting code examples and technical content"
        )

        result = extract_text_from_file(
            str(get_test_file()),
            options=options
        )

        assert result.success is True
        assert result.text is not None

    def test_extract_with_all_options(self):
        """Test extraction with chunking and parsing instructions"""
        options = ExtractionOptions(
            chunk_size=256,
            parsing_instructions="Pay special attention to code blocks and technical terminology"
        )

        result = extract_text_from_file(
            str(get_test_file()),
            options=options
        )

        assert result.success is True
        assert result.chunks is not None
        assert len(result.chunks) > 0


class TestAsyncIntegration:
    """Integration tests for async client"""

    @pytest.mark.asyncio
    async def test_extract_text_from_file_async_simple(self):
        """Test simple async extraction from file"""
        result = await extract_text_from_file_async(str(get_test_file()))

        assert result.success is True
        assert result.text is not None
        assert len(result.text) > 0
        print(f"\n✓ Async: Extracted {len(result.text)} characters")

    @pytest.mark.asyncio
    async def test_extract_text_async_from_bytes(self):
        """Test async extraction from bytes"""
        test_file = get_test_file()
        with open(test_file, "rb") as f:
            file_bytes = f.read()

        result = await extract_text_async(
            file_bytes=file_bytes,
            file_name=test_file.name
        )

        assert result.success is True
        assert result.text is not None

    @pytest.mark.asyncio
    async def test_extract_async_with_chunking(self):
        """Test async extraction with chunking"""
        options = ExtractionOptions(
            chunk_size=512
        )

        result = await extract_text_from_file_async(
            str(get_test_file()),
            options=options
        )

        assert result.success is True
        assert result.chunks is not None
        assert len(result.chunks) > 0
