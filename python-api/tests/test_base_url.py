"""
Where requests go: api.vectorize.io/v1/org/{org_id} by default, or a base URL as given (Hindsight
Inference, where the organization comes from the key and isn't in the path).
"""

import os
from unittest.mock import Mock, patch

import pytest

from vectorize_iris import VectorizeIrisError, extract_text, extract_text_async
from vectorize_iris.config import resolve

HINDSIGHT = "https://inference.hindsight.vectorize.io/v1"
UPLOAD_URL = "https://storage.example.com/signed"
DONE = {"ready": True, "data": {"success": True, "text": "hello", "chunks": ["hello"],
                                "metadata": None, "usage": {"irisPages": 1}, "error": None}}


@pytest.fixture(autouse=True)
def clean_env():
    keys = ("VECTORIZE_TOKEN", "VECTORIZE_ORG_ID", "VECTORIZE_IRIS_BASE_URL")
    with patch.dict(os.environ, {}, clear=False):
        for k in keys:
            os.environ.pop(k, None)
        yield


def response(status, body=None):
    r = Mock()
    r.status_code = status
    r.json.return_value = body or {}
    r.text = str(body)
    return r


def fake_requests():
    calls = []

    def post(url, **kw):
        calls.append(("POST", url, kw.get("headers")))
        if url.endswith("/files"):
            return response(200, {"fileId": "f1", "uploadUrl": UPLOAD_URL})
        return response(200, {"message": "Extraction started.", "extractionId": "e1"})

    def put(url, **kw):
        calls.append(("PUT", url, kw.get("headers")))
        return response(200)

    def get(url, **kw):
        calls.append(("GET", url, kw.get("headers")))
        return response(200, DONE)

    m = Mock(post=post, put=put, get=get)
    return m, calls


class TestResolve:
    def test_default_is_api_vectorize_io_with_the_org(self):
        assert resolve("t", "org-1", None) == ("t", "https://api.vectorize.io/v1/org/org-1")

    def test_base_url_is_used_as_given_and_needs_no_org(self):
        assert resolve("hsk_x", None, HINDSIGHT + "/") == ("hsk_x", HINDSIGHT)

    def test_base_url_from_the_environment(self):
        os.environ.update(VECTORIZE_TOKEN="hsk_x", VECTORIZE_IRIS_BASE_URL=HINDSIGHT)
        assert resolve(None, None, None) == ("hsk_x", HINDSIGHT)

    def test_argument_beats_the_environment(self):
        os.environ.update(VECTORIZE_IRIS_BASE_URL="https://other.example/v1")
        assert resolve("t", None, HINDSIGHT)[1] == HINDSIGHT

    def test_without_a_base_url_the_org_is_still_required(self):
        with pytest.raises(VectorizeIrisError, match="VECTORIZE_ORG_ID"):
            resolve("t", None, None)

    def test_a_token_is_always_required(self):
        with pytest.raises(VectorizeIrisError, match="Missing credentials"):
            resolve(None, None, HINDSIGHT)


class TestSyncClient:
    def test_hindsight_base_url_gets_every_call_without_an_org(self):
        fake, calls = fake_requests()
        with patch("vectorize_iris.client.requests", fake):
            result = extract_text(b"%PDF", "a.pdf", api_token="hsk_x", base_url=HINDSIGHT, poll_interval=0)
        assert result.text == "hello"
        api = [(m, u) for m, u, _ in calls if m != "PUT"]
        assert api == [("POST", f"{HINDSIGHT}/files"), ("POST", f"{HINDSIGHT}/extraction"),
                       ("GET", f"{HINDSIGHT}/extraction/e1")]
        assert all(h["Authorization"] == "Bearer hsk_x" for m, _, h in calls if m != "PUT")

    def test_default_is_unchanged(self):
        fake, calls = fake_requests()
        with patch("vectorize_iris.client.requests", fake):
            extract_text(b"%PDF", "a.pdf", api_token="t", org_id="org-1", poll_interval=0)
        assert calls[0][1] == "https://api.vectorize.io/v1/org/org-1/files"


class FakeAiohttpResponse:
    def __init__(self, status, body=None):
        self.status = status
        self._body = body or {}

    async def json(self):
        return self._body

    async def text(self):
        return str(self._body)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class FakeSession:
    calls = []

    def __init__(self, *a, **kw):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def post(self, url, **kw):
        FakeSession.calls.append(("POST", url))
        if url.endswith("/files"):
            return FakeAiohttpResponse(200, {"fileId": "f1", "uploadUrl": UPLOAD_URL})
        return FakeAiohttpResponse(200, {"message": "Extraction started.", "extractionId": "e1"})

    def put(self, url, **kw):
        FakeSession.calls.append(("PUT", url))
        return FakeAiohttpResponse(200)

    def get(self, url, **kw):
        FakeSession.calls.append(("GET", url))
        return FakeAiohttpResponse(200, DONE)


@pytest.mark.asyncio
class TestAsyncClient:
    async def test_hindsight_base_url_from_the_environment(self):
        FakeSession.calls = []
        os.environ.update(VECTORIZE_TOKEN="hsk_x", VECTORIZE_IRIS_BASE_URL=HINDSIGHT)
        with patch("vectorize_iris.async_client.aiohttp.ClientSession", FakeSession):
            result = await extract_text_async(b"%PDF", "a.pdf", poll_interval=0)
        assert result.text == "hello"
        assert [c for c in FakeSession.calls if c[0] != "PUT"] == [
            ("POST", f"{HINDSIGHT}/files"), ("POST", f"{HINDSIGHT}/extraction"), ("GET", f"{HINDSIGHT}/extraction/e1")]
