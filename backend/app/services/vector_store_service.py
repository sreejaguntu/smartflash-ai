from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.database import get_sessionmaker
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService

settings = get_settings()


class VectorStoreService:

    @classmethod
    def add_chunks(cls, document_id: str, chunks: list[str]) -> int:
        """Embed and store chunks for a document. Returns the number stored."""
        if not chunks:
            return 0

        embeddings = EmbeddingService.embed_texts(chunks)

        session_factory = get_sessionmaker()
        with session_factory() as session:
            # Replace any existing chunks for this document (idempotent re-index).
            session.execute(delete(Chunk).where(Chunk.document_id == document_id))

            session.add_all(
                Chunk(
                    document_id=document_id,
                    chunk_index=index,
                    content=content,
                    embedding=embedding,
                )
                for index, (content, embedding) in enumerate(zip(chunks, embeddings))
            )
            session.commit()

        return len(chunks)

    @classmethod
    def search(
        cls,
        query: str,
        top_k: int | None = None,
        document_id: str | None = None,
    ) -> list[dict]:
        """Return the most semantically similar chunks to the query."""
        top_k = top_k or settings.default_top_k
        query_embedding = EmbeddingService.embed_text(query)

        distance = Chunk.embedding.cosine_distance(query_embedding)

        statement = select(Chunk, distance.label("distance"))
        if document_id:
            statement = statement.where(Chunk.document_id == document_id)
        statement = statement.order_by(distance).limit(top_k)

        session_factory = get_sessionmaker()
        with session_factory() as session:
            rows = session.execute(statement).all()

        return [
            {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                # Cosine similarity = 1 - cosine distance.
                "score": 1.0 - float(dist),
            }
            for chunk, dist in rows
        ]
