from pathlib import Path
import re
import uuid

from fastapi import UploadFile, HTTPException


class UploadService:

    # Allowed file types
    ALLOWED_EXTENSIONS = [".pdf"]

    # Maximum file size (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Upload directory
    UPLOAD_DIR = Path("uploads")

    _DOCUMENT_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")

    @classmethod
    async def save_file(cls, file: UploadFile):

        # Create uploads folder if it doesn't exist
        cls.UPLOAD_DIR.mkdir(exist_ok=True)

        # -------------------------
        # Validate extension
        # -------------------------
        extension = Path(file.filename or "").suffix.lower()

        if extension not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        # -------------------------
        # Validate file size
        # -------------------------
        contents = await file.read()

        if len(contents) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 10 MB."
            )

        if not contents.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail="File is not a valid PDF."
            )

        # -------------------------
        # Save file
        # -------------------------
        # Store under a generated id, never the client-supplied name (path traversal / overwrites).
        document_id = uuid.uuid4().hex
        file_path = cls.UPLOAD_DIR / f"{document_id}{extension}"
        file_path.write_bytes(contents)

        return {
            "document_id": document_id,
            "filename": Path(file.filename).name,
            "path": str(file_path)
        }

    @classmethod
    def resolve_path(cls, document_id: str) -> Path:
        """Return the stored PDF path for a document id, or raise 404."""
        if not cls._DOCUMENT_ID_PATTERN.match(document_id):
            raise HTTPException(status_code=400, detail="Invalid document_id.")

        file_path = cls.UPLOAD_DIR / f"{document_id}.pdf"
        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="Document not found.")

        return file_path