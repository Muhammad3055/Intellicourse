from pydantic import BaseModel, Field
from typing import List, Literal

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)

class QueryResponse(BaseModel):
    answer: str
    source_tool: Literal["rag", "web"]
    context_snippets: List[str] = []
    used_docs: List[str] = []
    used_urls: List[str] = []
