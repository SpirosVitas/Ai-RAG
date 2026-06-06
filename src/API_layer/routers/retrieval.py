from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.API_layer.security import (
    get_current_user,
)

from src.RAG_layer.engine import (
    rag_engine,
)

router = APIRouter(
    prefix="/retrieval",
    tags=["Semantic Search & RAG"],
)


class QueryRequest(BaseModel):

    query: str = Field(
        ...,
        example="What are the audit requirements under DORA Article 17?"
    )


class QueryResponse(BaseModel):

    answer: str
    citations: list[str]


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def ask_compliance_assistant(
    request: QueryRequest,
    current_user: str = Depends(
        get_current_user
    ),
):

    result = rag_engine.answer_query(
        request.query
    )

    return result