from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    document_id: str = Field(..., description="Id returned by /upload.")


class IndexResponse(BaseModel):
    document_id: str
    chunks_indexed: int


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    indexed: bool
    chunks_indexed: int


class SearchResult(BaseModel):
    document_id: str
    chunk_index: int
    content: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
