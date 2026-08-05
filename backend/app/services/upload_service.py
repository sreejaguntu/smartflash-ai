from pathlib import Path
import shutil
from fastapi import UploadFile, HTTPException


class UploadService:

    # Allowed file types
    ALLOWED_EXTENSIONS = [".pdf"]

    # Maximum file size (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Upload directory
    UPLOAD_DIR = Path("uploads")

    @classmethod
    async def save_file(cls, file: UploadFile):

        # Create uploads folder if it doesn't exist
        cls.UPLOAD_DIR.mkdir(exist_ok=True)

        # -------------------------
        # Validate extension
        # -------------------------
        extension = Path(file.filename).suffix.lower()

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

        # Reset pointer after reading
        file.file.seek(0)

        # -------------------------
        # Save file
        # -------------------------
        file_path = cls.UPLOAD_DIR / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "filename": file.filename,
            "path": str(file_path)
        }