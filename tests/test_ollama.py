import httpx
import pytest

from aegis.targets.ollama import OllamaTarget


def test_ollama_target_defaults():
    target = OllamaTarget()

    assert target.model_name == "llama3.2:3b"
    assert target.base_url == "http://localhost:11434"


def test_ollama_target_custom_configuration():
    target = OllamaTarget(
        model="mistral",
        base_url="http://127.0.0.1:11434/",
    )

    assert target.model_name == "mistral"
    assert target.base_url == "http://127.0.0.1:11434"


@pytest.mark.asyncio
async def test_ollama_target_generate(monkeypatch):
    captured = {}

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "response": "Hello from Ollama",
            }

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            captured["timeout"] = kwargs.get("timeout")

        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

        async def post(
            self,
            url,
            json,
        ):
            captured["url"] = url
            captured["json"] = json
            return MockResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        MockAsyncClient,
    )

    target = OllamaTarget(
        model="llama3.2:3b",
        base_url="http://localhost:11434",
    )

    response = await target.generate(
        "Hello"
    )

    assert response == "Hello from Ollama"

    assert (
        captured["url"]
        == "http://localhost:11434/api/generate"
    )

    assert captured["json"] == {
        "model": "llama3.2:3b",
        "prompt": "Hello",
        "stream": False,
    }

    assert captured["timeout"] == 120.0


@pytest.mark.asyncio
async def test_ollama_target_generate_http_error(
    monkeypatch,
):
    class MockResponse:
        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "Server error",
                request=httpx.Request(
                    "POST",
                    "http://localhost:11434/api/generate",
                ),
                response=httpx.Response(
                    500,
                ),
            )

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            pass

        async def post(
            self,
            url,
            json,
        ):
            return MockResponse()

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        MockAsyncClient,
    )

    target = OllamaTarget()

    with pytest.raises(
        httpx.HTTPStatusError
    ):
        await target.generate(
            "Test prompt"
        )
