import fitz
from fastapi import HTTPException


class PDFService:

    @staticmethod
    def extract_text(pdf_path: str):
        try:
            document = fitz.open(pdf_path)
            extracted_text = ""
            for page in document:
                extracted_text += page.get_text()
            document.close()

            if not extracted_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="No readable text found."
                )

            return extracted_text

        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Unable to read PDF."
            )