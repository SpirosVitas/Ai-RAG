from src.config.settings import settings
from src.data_ingestion.embeddings import LocalEmbeddingModel
from src.data_ingestion.vector_store import ChromaVectorStore
from src.data_ingestion.retriever import AzureOpenAIChatLLM
from src.data_ingestion.rag_pipeline import RAGPipeline


embedder = LocalEmbeddingModel()

vector_store = ChromaVectorStore(
    persist_path=settings.VECTOR_DB_DIR,
    collection_name=settings.COLLECTION_NAME,
)

llm = AzureOpenAIChatLLM()

rag = RAGPipeline(
    vector_store=vector_store,
    llm=llm,
    embedder=embedder,
)