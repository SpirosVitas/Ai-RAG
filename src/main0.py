# # -------------------------------------------------------

# """
# file: src/main0.py
# """

# import json
# import os
# from src.config.settings import settings
# from src.data_ingestion.pdf_ingestion import extract_pdf_pages
# from src.data_ingestion.chunking import create_chunks
# from src.data_ingestion.embeddings import LocalEmbeddingModel
# from src.data_ingestion.vector_store import ChromaVectorStore
# from src.data_ingestion.retriever import AzureOpenAIChatLLM
# from src.data_ingestion.context_builder import build_context
# from src.data_ingestion.rag_pipeline import RAGPipeline


# def ingest_all_pdfs(
#     embedder: LocalEmbeddingModel,
#     vector_store: ChromaVectorStore,
# ):

#     pdf_files = list(settings.DOCUMENTS_DIR.glob("*.pdf"))

#     total_chunks = 0

#     # Holders to track structural data for Silver and Gold layers
#     silver_records = []
#     gold_records = []

#     for pdf_path in pdf_files:

#         print(f"\nProcessing: {pdf_path.name}")

#         # Extract the pure CELEX ID string from the filename (e.g., '32022R2554_EN' -> '32022R2554')
#         celex_id_val = pdf_path.stem.split('_')[0]

#         # 1. Extract PDF
#         pages = extract_pdf_pages(str(pdf_path))

#         # 2. Chunk
#         chunks = create_chunks(pages)

#         # 3. Embed
#         embedded_chunks = embedder.embed_chunks(chunks)

#         # 4. Store in vector DB
#         vector_store.add_chunks(embedded_chunks)

#         # --- DATA PREPARATION FOR YOUR DATABRICKS FILES ---
#         for idx, chunk in enumerate(chunks):
#             chunk_text = chunk.text if hasattr(chunk, 'text') else str(chunk)
#             chunk_id = f"{pdf_path.stem}_{idx}"
            
#             # Key changed from document_id to celex_id
#             silver_records.append({
#                 "chunk_id": chunk_id,
#                 "celex_id": celex_id_val,
#                 "text_content": chunk_text
#             })

#         for idx, embedded_chunk in enumerate(embedded_chunks):
#             vector = embedded_chunk.embedding if hasattr(embedded_chunk, 'embedding') else embedded_chunk.get('embedding')
#             chunk_text = embedded_chunk.text if hasattr(embedded_chunk, 'text') else str(embedded_chunk)
#             chunk_id = f"{pdf_path.stem}_{idx}"
            
#             # Key changed from document_id to celex_id
#             vector_floats = [float(v) for v in vector]
#             gold_records.append({
#                 "chunk_id": chunk_id,
#                 "celex_id": celex_id_val,
#                 "text_content": chunk_text,
#                 "embeddings": vector_floats
#             })

#         total_chunks += len(chunks)

#         print(f"Chunks: {len(chunks)}")

#     print(f"\nTOTAL CHUNKS INDEXED LOCALLY: {total_chunks}")
    
#     # -----------------------------------------------------------------
#     # Exporting Staging Files for Databricks Bundle Upload
#     # -----------------------------------------------------------------
#     project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
#     target_data_dir = os.path.join(project_root, "data")
    
#     os.makedirs(target_data_dir, exist_ok=True)
    
#     silver_file_path = os.path.join(target_data_dir, "silver_staging.json")
#     gold_file_path = os.path.join(target_data_dir, "gold_staging.json")
    
#     with open(silver_file_path, "w", encoding="utf-8") as f:
#         json.dump(silver_records, f, ensure_ascii=False, indent=4)
#     print(f"[Local Export] Saved Silver staging data to: {silver_file_path}")
        
#     with open(gold_file_path, "w", encoding="utf-8") as f:
#         json.dump(gold_records, f, ensure_ascii=False, indent=4)
#     print(f"[Local Export] Saved Gold staging data to: {gold_file_path}")
    
#     return silver_records, gold_records


# def main():

#     # ----------------------------
#     # Components
#     # ----------------------------

#     embedder = LocalEmbeddingModel()

#     vector_store = ChromaVectorStore(
#         persist_path=settings.VECTOR_DB_DIR,
#         collection_name=settings.COLLECTION_NAME,
#     )

#     llm = AzureOpenAIChatLLM()

#     # ----------------------------
#     # INGESTION PHASE
#     # ----------------------------

#     existing_chunks = vector_store.count()
    
#     print("\n[Info] Forcing PDF ingestion phase...")
#     ingest_all_pdfs(embedder, vector_store)

#     # ----------------------------
#     # RETRIEVAL PHASE
#     # ----------------------------

#     rag = RAGPipeline(
#         vector_store=vector_store,
#         llm=llm,
#         embedder=embedder
#     )

#     # ----------------------------
#     # QUERY LOOP
#     # ----------------------------

#     while True:

#         question = input("\nAsk a question (or 'exit'): ")

#         if question.lower() in ["exit", "quit"]:
#             break

#         result = rag.ask(question)

#         print("\nANSWER:\n")
#         print(result["answer"])

#         print("\nSOURCES:\n")

#         for i, src in enumerate(result["sources"], start=1):

#             meta = src["metadata"]

#             print(
#                 f"[Source {i}] "
#                 f"{meta.get('document_id', 'N/A')} | "
#                 f"distance={src['distance']:.4f}"
#             )


# if __name__ == "__main__":
#     main()

# -------------------------------------------------------



"""
file: src/mainprogram.py
This file is the main entry point for the application. It orchestrates the data ingestion.
It also contains a simple query loop for testing the RAG pipeline in a console environment.
Runs once to ingest the data or when a new PDF is added to the documents.
"""
 
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
 
 
if __name__ == "__main__":
    main()


"""
uv run python -m src.main0
"""