from openai import OpenAI

from app.core.config import get_settings

settings = get_settings()


class EmbeddingService:

    # Keeps each request well under the API's per-request input/token limits.
    BATCH_SIZE = 100

    _client: OpenAI | None = None

    @classmethod
    def _get_client(cls) -> OpenAI:
        if cls._client is None:
            settings.require_openai()
            cls._client = OpenAI(api_key=settings.openai_api_key)
        return cls._client

    @classmethod
    def embed_texts(cls, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector per input text (order preserved)."""
        if not texts:
            return []

        client = cls._get_client()
        embeddings: list[list[float]] = []
        for start in range(0, len(texts), cls.BATCH_SIZE):
            response = client.embeddings.create(
                model=settings.embedding_model,
                input=texts[start:start + cls.BATCH_SIZE],
            )
            embeddings.extend(item.embedding for item in response.data)
        return embeddings

    @classmethod
    def embed_text(cls, text: str) -> list[float]:
        return cls.embed_texts([text])[0]
