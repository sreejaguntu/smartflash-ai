import logging

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.core.database import init_db
from app.services.ingestion_service import IngestionService
from app.services.upload_service import UploadService
from app.services.vector_store_service import VectorStoreService
from app.schemas.retrieval import (
    IndexRequest,
    IndexResponse,
    SearchResponse,
    SearchResult,
    UploadResponse,
)

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title="SmartFlash AI")


@app.on_event("startup")
def on_startup() -> None:
    # Only initialise the vector store when a database is configured, so the
    # app can still boot for upload/extract during local development.
    if settings.database_url:
        init_db()
    else:
        logger.warning("DATABASE_URL not set; vector store endpoints are disabled.")


@app.get("/")
def home():
    return {"message": "Welcome to SmartFlash AI!"}


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    result = await UploadService.save_file(file)

    # Without a database, just store the file; it can be indexed later via /index.
    chunks_indexed = 0
    if settings.database_url:
        chunks_indexed = await run_in_threadpool(
            IngestionService.ingest, result["document_id"], result["path"]
        )

    return UploadResponse(
        document_id=result["document_id"],
        filename=result["filename"],
        indexed=bool(settings.database_url),
        chunks_indexed=chunks_indexed,
    )


@app.get("/extract-text")
def extract_text(document_id: str):
    file_path = UploadService.resolve_path(document_id)
    chunks = IngestionService.build_chunks(str(file_path))
    return {
        "message": "Text extracted successfully!",
        "chunk_count": len(chunks),
        "chunks": chunks,
    }


@app.post("/index", response_model=IndexResponse)
def index_document(request: IndexRequest):
    file_path = UploadService.resolve_path(request.document_id)
    count = IngestionService.ingest(request.document_id, str(file_path))
    return IndexResponse(document_id=request.document_id, chunks_indexed=count)


@app.get("/search", response_model=SearchResponse)
def search(
    query: str = Query(..., description="Natural-language search query."),
    top_k: int | None = Query(None, ge=1, le=50),
    document_id: str | None = Query(None),
):
    results = VectorStoreService.search(query, top_k=top_k, document_id=document_id)
    return SearchResponse(
        query=query,
        results=[SearchResult(**r) for r in results],
    )