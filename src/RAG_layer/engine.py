from src.data_ingestion.embeddings import LocalEmbeddingModel
from src.data_ingestion.vector_store import ChromaVectorStore
from src.data_ingestion.retriever import AzureOpenAIChatLLM
from src.config.settings import settings


class RAGEngine:

    def __init__(self):

        self.embedding_model = LocalEmbeddingModel()

        self.vector_store = ChromaVectorStore(
            persist_path=settings.VECTOR_DB_DIR,
        )

        self.llm = AzureOpenAIChatLLM()

    def answer_query(
        self,
        question: str,
    ) -> dict:

        query_embedding = (
            self.embedding_model.embed_query(
                question
            )
        )

        retrieved_chunks = (
            self.vector_store.search(
                query_embedding=query_embedding,
                top_k=settings.TOP_K,
            )
        )

        context_parts = []
        citations = []

        for idx, chunk in enumerate(
            retrieved_chunks,
            start=1,
        ):

            source = (
                chunk["metadata"]
                .get(
                    "regulation_title",
                    "Unknown Source",
                )
            )

            citations.append(source)

            context_parts.append(
                f"""
[Source {idx}]
Document: {source}

Content:
{chunk['content']}
"""
            )

        context = "\n\n".join(
            context_parts
        )

        answer = self.llm.generate(
            question=question,
            context=context,
        )

        return {
            "answer": answer,
            "citations": list(set(citations)),
        }


rag_engine = RAGEngine()