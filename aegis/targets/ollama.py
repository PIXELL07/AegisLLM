import httpx

from aegis.targets.base import Target


class OllamaTarget(Target):
    """Target adapter for locally running Ollama models."""

    def __init__(
        self,
        model: str = "llama3.2:3b",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    @property
    def model_name(self) -> str:
        return self.model

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

            return data["response"]