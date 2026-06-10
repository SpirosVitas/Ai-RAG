"""
rag_pipeline.py
"""

from src.ingestion.context_builder import build_context
from .llm import AzureOpenAIChatLLM
from src.ingestion.vector_store import ChromaVectorStore


class RAGPipeline:

    def __init__(
        self,
        vector_store : ChromaVectorStore,
        llm: AzureOpenAIChatLLM,
        embedder,
    ):
        self.vector_store = vector_store
        self.llm = llm
        self.embedder = embedder

    def ask(
        self,
        question: str,
    ) -> dict:

        query_embedding = self.embedder.embed_query(question)

        retrieved_chunks = self.vector_store.search(
            query_embedding = query_embedding
        )

        context = build_context(retrieved_chunks)

        answer = self.llm.generate(
            question=question,
            context=context,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": retrieved_chunks,
        }