from fastapi import FastAPI
from src.API_layer.routers import auth, ingestion, retrieval
from src.config.settings import settings
from src.data_ingestion.pdf_ingestion import extract_pdf_pages
from src.data_ingestion.chunking import create_chunks
from src.data_ingestion.embeddings import LocalEmbeddingModel
from src.data_ingestion.vector_store import ChromaVectorStore
from src.data_ingestion.retriever import AzureOpenAIChatLLM
from src.data_ingestion.context_builder import build_context
from src.data_ingestion.rag_pipeline import RAGPipeline


def ingest_all_pdfs(
    embedder: LocalEmbeddingModel,
    vector_store: ChromaVectorStore,
):

    pdf_files = list(settings.DOCUMENTS_DIR.glob("*.pdf"))

    total_chunks = 0

    for pdf_path in pdf_files:

        print(f"\nProcessing: {pdf_path.name}")

        # 1. Extract PDF
        pages = extract_pdf_pages(str(pdf_path))

        # 2. Chunk
        chunks = create_chunks(pages)

        # 3. Embed
        embedded_chunks = embedder.embed_chunks(chunks)

        # 4. Store in vector DB
        vector_store.add_chunks(embedded_chunks)

        total_chunks += len(chunks)

        print(f"Chunks: {len(chunks)}")

    print(f"\nTOTAL CHUNKS INDEXED: {total_chunks}")


def main():

    # ----------------------------
    # Components
    # ----------------------------

    embedder = LocalEmbeddingModel()

    vector_store = ChromaVectorStore(
        persist_path=settings.VECTOR_DB_DIR,
        collection_name=settings.COLLECTION_NAME,
    )

    llm = AzureOpenAIChatLLM()

    # ----------------------------
    # INGESTION PHASE
    # ----------------------------



    existing_chunks = vector_store.count()
    
    if existing_chunks > 0:
        print(f"\n[Info] Vector DB already contains {existing_chunks} chunks. Skipping PDF ingestion.")
    else:
        print("\n[Info] Vector DB is empty. Starting PDF ingestion phase...")
        ingest_all_pdfs(embedder, vector_store)

    # ----------------------------
    # RETRIEVAL PHASE
    # ----------------------------


    rag = RAGPipeline(
        vector_store=vector_store,
        llm=llm,
        embedder=embedder
    )

    # ----------------------------
    # QUERY LOOP
    # ----------------------------

    while True:

        question = input("\nAsk a question (or 'exit'): ")

        if question.lower() in ["exit", "quit"]:
            break

        result = rag.ask(question)

        print("\nANSWER:\n")
        print(result["answer"])

        print("\nSOURCES:\n")

        for i, src in enumerate(result["sources"], start=1):

            meta = src["metadata"]

            print(
                f"[Source {i}] "
                f"{meta.get('document_id')} | "
                f"{meta.get('article_reference')} | "
                f"distance={src['distance']:.4f}"
            )


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Knowledge Engineering Platform for EU Regulations Compliance",
    version="0.1.0",
    docs_url="/docs",       # Swagger UI URL
    redoc_url="/redoc"
)

# Σύνδεση των Routers με το API Versioning prefix (/api/v1)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(ingestion.router, prefix=settings.API_V1_STR)
app.include_router(retrieval.router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the EU Regulatory Compliance Assistant API",
        "docs": "/docs"
    }