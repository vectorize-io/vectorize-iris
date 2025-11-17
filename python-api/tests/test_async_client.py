"""
Unit tests for async client
"""

import os
import pytest
from unittest.mock import Mock, patch, mock_open, AsyncMock
from pathlib import Path
import asyncio

from vectorize_iris import extract_text_async, VectorizeIrisError


@pytest.fixture
def mock_env():
    """Set up mock environment variables"""
    with patch.dict(os.environ, {
        'VECTORIZE_API_TOKEN': 'test-token',
        'VECTORIZE_ORG_ID': 'test-org-id'
    }):
        yield


@pytest.fixture
def mock_file():
    """Mock file operations"""
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.stat') as mock_stat, \
         patch('builtins.open', mock_open(read_data=b'test file content')):
        mock_stat.return_value.st_size = 100
        yield


class TestExtractTextAsync:
    """Test extract_text_async function"""

    @pytest.mark.asyncio
    async def test_missing_credentials(self):
        """Test that missing credentials raises an error"""
        with pytest.raises(VectorizeIrisError, match="Missing credentials"):
            await extract_text_async("test.pdf")

    @pytest.mark.asyncio
    async def test_file_not_found(self, mock_env):
        """Test that non-existent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError, match="File not found"):
            await extract_text_async("/nonexistent/file.pdf")

    @pytest.mark.asyncio
    async def test_successful_extraction(self, mock_env, mock_file):
        """Test successful text extraction flow"""
        # Mock aiohttp responses
        mock_session = AsyncMock()

        # Mock upload start
        mock_upload_response = AsyncMock()
        mock_upload_response.status = 200
        mock_upload_response.json = AsyncMock(return_value={
            'fileId': 'file-123',
            'uploadUrl': 'https://upload.example.com'
        })
        mock_upload_response.__aenter__ = AsyncMock(return_value=mock_upload_response)
        mock_upload_response.__aexit__ = AsyncMock(return_value=None)

        # Mock file upload
        mock_put_response = AsyncMock()
        mock_put_response.status = 200
        mock_put_response.__aenter__ = AsyncMock(return_value=mock_put_response)
        mock_put_response.__aexit__ = AsyncMock(return_value=None)

        # Mock extraction start
        mock_extraction_response = AsyncMock()
        mock_extraction_response.status = 200
        mock_extraction_response.json = AsyncMock(return_value={
            'extractionId': 'extraction-123'
        })
        mock_extraction_response.__aenter__ = AsyncMock(return_value=mock_extraction_response)
        mock_extraction_response.__aexit__ = AsyncMock(return_value=None)

        # Mock status checks
        mock_status_response_1 = AsyncMock()
        mock_status_response_1.status = 200
        mock_status_response_1.json = AsyncMock(return_value={'status': 'processing'})
        mock_status_response_1.__aenter__ = AsyncMock(return_value=mock_status_response_1)
        mock_status_response_1.__aexit__ = AsyncMock(return_value=None)

        mock_status_response_2 = AsyncMock()
        mock_status_response_2.status = 200
        mock_status_response_2.json = AsyncMock(return_value={
            'status': 'completed',
            'result': {'text': 'Extracted text content'}
        })
        mock_status_response_2.__aenter__ = AsyncMock(return_value=mock_status_response_2)
        mock_status_response_2.__aexit__ = AsyncMock(return_value=None)

        # Set up session mock
        mock_session.post = Mock(side_effect=[
            mock_upload_response,
            mock_extraction_response
        ])
        mock_session.put = Mock(return_value=mock_put_response)
        mock_session.get = Mock(side_effect=[
            mock_status_response_1,
            mock_status_response_2
        ])
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('vectorize_iris.async_client.aiohttp.ClientSession', return_value=mock_session):
            result = await extract_text_async("test.pdf", poll_interval=0.1)

        assert result == 'Extracted text content'

    @pytest.mark.asyncio
    async def test_extraction_failure(self, mock_env, mock_file):
        """Test handling of extraction failure"""
        mock_session = AsyncMock()

        # Mock successful upload
        mock_upload_response = AsyncMock()
        mock_upload_response.status = 200
        mock_upload_response.json = AsyncMock(return_value={
            'fileId': 'file-123',
            'uploadUrl': 'https://upload.example.com'
        })
        mock_upload_response.__aenter__ = AsyncMock(return_value=mock_upload_response)
        mock_upload_response.__aexit__ = AsyncMock(return_value=None)

        mock_put_response = AsyncMock()
        mock_put_response.status = 200
        mock_put_response.__aenter__ = AsyncMock(return_value=mock_put_response)
        mock_put_response.__aexit__ = AsyncMock(return_value=None)

        mock_extraction_response = AsyncMock()
        mock_extraction_response.status = 200
        mock_extraction_response.json = AsyncMock(return_value={
            'extractionId': 'extraction-123'
        })
        mock_extraction_response.__aenter__ = AsyncMock(return_value=mock_extraction_response)
        mock_extraction_response.__aexit__ = AsyncMock(return_value=None)

        # Mock failed extraction
        mock_status_response = AsyncMock()
        mock_status_response.status = 200
        mock_status_response.json = AsyncMock(return_value={
            'status': 'failed',
            'error': 'Invalid file format'
        })
        mock_status_response.__aenter__ = AsyncMock(return_value=mock_status_response)
        mock_status_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.post = Mock(side_effect=[
            mock_upload_response,
            mock_extraction_response
        ])
        mock_session.put = Mock(return_value=mock_put_response)
        mock_session.get = Mock(return_value=mock_status_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch('vectorize_iris.async_client.aiohttp.ClientSession', return_value=mock_session):
            with pytest.raises(VectorizeIrisError, match="Extraction failed: Invalid file format"):
                await extract_text_async("test.pdf", poll_interval=0.1)
