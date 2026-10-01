import fitz
from fastapi import HTTPException


class PDFService:

    @staticmethod
    def extract_text(pdf_path: str):
        try:
            with fitz.open(pdf_path) as document:
                # Blank line between pages so words don't merge across page boundaries.
                extracted_text = "\n\n".join(page.get_text() for page in document)
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Unable to read PDF."
            )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found."
            )

        return extracted_text