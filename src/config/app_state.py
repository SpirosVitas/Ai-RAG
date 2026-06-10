from src.config.settings import settings
from src.ingestion.embeddings import LocalEmbeddingModel
from src.ingestion.vector_store import ChromaVectorStore
from src.ingestion.llm import AzureOpenAIChatLLM
from src.ingestion.rag_pipeline import RAGPipeline


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