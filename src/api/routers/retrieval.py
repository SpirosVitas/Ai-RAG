from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
import src.config.app_state
from src.api.security import (get_current_user)


router = APIRouter(
    prefix="/retrieval",
    tags=["RAG"],
)


#class QueryRequest(BaseModel):
#    query: str

class QueryRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=5000
    )


class QueryResponse(BaseModel):
    answer: str
    sources: list


@router.post(
    "/query",
    response_model=QueryResponse,
)
async def query_documents(
    request: QueryRequest,
    user=Depends(get_current_user)
):

    result = src.config.app_state.rag.ask(
        request.query
    )

#    return {
#        "answer": result["answer"],
#        "sources": result["sources"],
#    }

    return QueryResponse(
    answer=result["answer"],
    sources=result["sources"],
)