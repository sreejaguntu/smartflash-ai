from app.services.pdf_service import PDFService
from app.services.vector_store_service import VectorStoreService
from app.utils.text_chunker import TextChunker
from app.utils.text_cleaner import TextCleaner


class IngestionService:

    @staticmethod
    def build_chunks(pdf_path: str) -> list[str]:
        """Extract -> clean -> chunk."""
        extracted_text = PDFService.extract_text(pdf_path)
        cleaned_text = TextCleaner.clean(extracted_text)
        return TextChunker.chunk(cleaned_text)

    @classmethod
    def ingest(cls, document_id: str, pdf_path: str) -> int:
        """Run the full pipeline (extract -> clean -> chunk -> embed -> store)."""
        chunks = cls.build_chunks(pdf_path)
        return VectorStoreService.add_chunks(document_id, chunks)
