"""
vector_store.py

Local vector database using ChromaDB.

Current:
    - ChromaDB

Future:
    - Databricks Vector Search
    - Azure AI Search
"""

from pathlib import Path

import chromadb
from chromadb.config import Settings

from src.config.settings import settings


class ChromaVectorStore:

    def __init__(
        self,
        persist_path: Path,
        collection_name: str = settings.COLLECTION_NAME,
    ):

        self.client = chromadb.PersistentClient(
            path=str(persist_path),
            settings=Settings(
                anonymized_telemetry=False
            ),
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "hnsw:space": "cosine"
                },
            )
        )



    def add_chunks(
        self,
        embedded_chunks: list[dict],
    ) -> None:
        """
        Store embedded chunks in Chroma.
        """
        # --- DEDUPLICATION LOGIC ---
        seen_ids = set()
        unique_chunks = []
        
        for chunk in embedded_chunks:
            chunk_id = chunk.get("chunk_id")
            if chunk_id not in seen_ids:
                seen_ids.add(chunk_id)
                unique_chunks.append(chunk)
            else:
                print(f"[Warning] Skipping duplicate chunk_id encountered in batch: {chunk_id}")
                
        embedded_chunks = unique_chunks
        # ----------------------------

        ids = [
            chunk["chunk_id"]
            for chunk in embedded_chunks
        ]

        documents = [
            chunk["content"]
            for chunk in embedded_chunks
        ]

        embeddings = [
            chunk["embedding"]
            for chunk in embedded_chunks
        ]

        metadatas = []

        for chunk in embedded_chunks:

            metadatas.append(
                {
                    "document_id":
                        chunk.get(
                            "document_id",
                            "",
                        ),

                    "source_file":
                        chunk.get(
                            "source_file",
                            "",
                        ),

                    "regulation_title":
                        chunk.get(
                            "regulation_title",
                            "",
                        ),

                    "issuing_authority":
                        chunk.get(
                            "issuing_authority",
                            "",
                        ),

                    "article_reference":
                        chunk.get(
                            "article_reference",
                            "",
                        ),

                    "chunk_index":
                        chunk.get(
                            "chunk_index",
                            0,
                        ),
                }
            )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = settings.TOP_K,
    ) -> list[dict]:
        """
        Semantic search.
        """

        results = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
        )

        retrieved = []

        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(ids)):

            retrieved.append(
                {
                    "chunk_id": ids[i],
                    "content": docs[i],
                    "metadata": metas[i],
                    "distance": distances[i],
                }
            )

        return retrieved

    def count(self) -> int:

        return self.collection.count()

    def reset(self) -> None:

        self.client.delete_collection(
            self.collection.name
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=settings.COLLECTION_NAME,
                metadata={
                    "hnsw:space": "cosine"
                },
            )
        )