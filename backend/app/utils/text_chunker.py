class TextChunker:

    # Default chunk size and overlap in words
    DEFAULT_CHUNK_SIZE = 200
    DEFAULT_OVERLAP = 40

    @classmethod
    def chunk(
        cls,
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ) -> list[str]:
        if not text or not text.strip():
            return []

        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be between 0 and chunk_size - 1.")

        words = text.split()

        chunks: list[str] = []
        step = chunk_size - overlap
        for start in range(0, len(words), step):
            chunks.append(" ".join(words[start:start + chunk_size]))
            # Stop once the window reaches the end; a further window would be fully overlapped.
            if start + chunk_size >= len(words):
                break

        return chunks
