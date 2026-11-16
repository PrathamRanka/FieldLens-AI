from pydantic import BaseModel, Field
from typing import Literal
class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    mode: Literal["auto", "rag", "analytics"] = "auto"
class Source(BaseModel):
    filename: str
    chunk_id: int
    excerpt: str
class ChatResponse(BaseModel):
    request_id: str
    answer: str
    sources: list[Source]
    metrics: dict
    route: str
class ApprovalRequest(BaseModel):
    action: str = Field(min_length=1, max_length=500)
    approved: bool
    approved_by: str = Field(min_length=2, max_length=120)
