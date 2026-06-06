from fastapi import APIRouter
from pydantic import BaseModel
import src.app_state
from src.API_layer.security import (get_current_user)


router = APIRouter(
    prefix="/retrieval",
    tags=["RAG"],
)


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    sources: list


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def query_documents(
    request: QueryRequest,
):

    result = src.app_state.rag.ask(
        request.query
    )

    return {
        "answer": result["answer"],
        "sources": result["sources"],
    }