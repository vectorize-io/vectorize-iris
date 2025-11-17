"""
Unit tests for vectorize_iris module
"""

import os
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import vectorize_iris
from vectorize_iris import extract_text, VectorizeIrisError


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


class TestExtractText:
    """Test extract_text function"""

    def test_missing_credentials(self):
        """Test that missing credentials raises an error"""
        with pytest.raises(VectorizeIrisError, match="Missing credentials"):
            extract_text("test.pdf")

    def test_file_not_found(self, mock_env):
        """Test that non-existent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError, match="File not found"):
            extract_text("/nonexistent/file.pdf")

    @patch('vectorize_iris.requests.post')
    @patch('vectorize_iris.requests.put')
    @patch('vectorize_iris.requests.get')
    def test_successful_extraction(self, mock_get, mock_put, mock_post, mock_env, mock_file):
        """Test successful text extraction flow"""
        # Mock upload start
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'fileId': 'file-123',
            'uploadUrl': 'https://upload.example.com'
        }

        # Mock file upload
        mock_put.return_value.status_code = 200

        # Mock extraction polling - first processing, then completed
        mock_get_response_1 = Mock()
        mock_get_response_1.status_code = 200
        mock_get_response_1.json.return_value = {'status': 'processing'}

        mock_get_response_2 = Mock()
        mock_get_response_2.status_code = 200
        mock_get_response_2.json.return_value = {
            'status': 'completed',
            'result': {'text': 'Extracted text content'}
        }

        mock_get.side_effect = [mock_get_response_1, mock_get_response_2]

        # Call extract_text with short poll interval for faster test
        result = extract_text("test.pdf", poll_interval=0.1)

        assert result == 'Extracted text content'
        assert mock_post.call_count == 2  # upload start + extraction start
        assert mock_put.call_count == 1   # file upload
        assert mock_get.call_count == 2   # status checks

    @patch('vectorize_iris.requests.post')
    def test_upload_failure(self, mock_post, mock_env, mock_file):
        """Test handling of upload failure"""
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = 'Bad request'

        with pytest.raises(VectorizeIrisError, match="Failed to start upload"):
            extract_text("test.pdf")

    @patch('vectorize_iris.requests.post')
    @patch('vectorize_iris.requests.put')
    def test_file_upload_failure(self, mock_put, mock_post, mock_env, mock_file):
        """Test handling of file upload failure"""
        # Mock successful upload start
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'fileId': 'file-123',
            'uploadUrl': 'https://upload.example.com'
        }

        # Mock failed file upload
        mock_put.return_value.status_code = 403
        mock_put.return_value.text = 'Forbidden'

        with pytest.raises(VectorizeIrisError, match="Failed to upload file"):
            extract_text("test.pdf")

    @patch('vectorize_iris.requests.post')
    @patch('vectorize_iris.requests.put')
    @patch('vectorize_iris.requests.get')
    def test_extraction_failure(self, mock_get, mock_put, mock_post, mock_env, mock_file):
        """Test handling of extraction failure"""
        # Mock successful upload
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'fileId': 'file-123',
            'uploadUrl': 'https://upload.example.com'
        }
        mock_put.return_value.status_code = 200

        # Mock failed extraction
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'status': 'failed',
            'error': 'Invalid file format'
        }

        with pytest.raises(VectorizeIrisError, match="Extraction failed: Invalid file format"):
            extract_text("test.pdf", poll_interval=0.1)

    @patch('vectorize_iris.requests.post')
    @patch('vectorize_iris.requests.put')
    @patch('vectorize_iris.requests.get')
    @patch('vectorize_iris.time.time')
    def test_extraction_timeout(self, mock_time, mock_get, mock_put, mock_post, mock_env, mock_file):
        """Test extraction timeout"""
        # Mock successful upload
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'fileId': 'file-123',
            'uploadUrl': 'https://upload.example.com'
        }
        mock_put.return_value.status_code = 200

        # Mock always processing status
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'status': 'processing'}

        # Mock timeout
        mock_time.side_effect = [0, 0, 400]  # Start time, first check, then timeout

        with pytest.raises(VectorizeIrisError, match="Extraction timed out"):
            extract_text("test.pdf", poll_interval=0.1, timeout=300)

    def test_custom_credentials(self, mock_file):
        """Test using custom credentials instead of env vars"""
        with patch('vectorize_iris.requests.post') as mock_post, \
             patch('vectorize_iris.requests.put') as mock_put, \
             patch('vectorize_iris.requests.get') as mock_get:

            # Mock successful flow
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                'fileId': 'file-123',
                'uploadUrl': 'https://upload.example.com'
            }
            mock_put.return_value.status_code = 200
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'status': 'completed',
                'result': {'text': 'Success'}
            }

            result = extract_text(
                "test.pdf",
                api_token="custom-token",
                org_id="custom-org",
                poll_interval=0.1
            )

            assert result == 'Success'

            # Verify custom credentials were used
            auth_header = mock_post.call_args[1]['headers']['Authorization']
            assert auth_header == 'Bearer custom-token'
