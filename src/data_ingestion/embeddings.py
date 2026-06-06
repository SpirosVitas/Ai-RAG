"""
embeddings.py

Embedding generation layer.

Current implementation:
- SentenceTransformers

Future replacements:
- Azure OpenAI
- Databricks Foundation Models
- Databricks Vector Search
"""

from sentence_transformers import SentenceTransformer

from src.config.settings import settings


class LocalEmbeddingModel:

    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL_NAME,
    ):
        self.model = SentenceTransformer(model_name)

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    def embed_query(
        self,
        text: str,
    ) -> list[float]:

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_chunks(
        self,
        chunks: list[dict],
    ) -> list[dict]:
        """
        Adds embeddings to chunk records.
        """

        texts = [
            chunk["content"]
            for chunk in chunks
        ]

        embeddings = self.embed_documents(texts)

        enriched_chunks = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
            strict=False,
        ):

            enriched_chunk = {
                **chunk,
                "embedding": embedding,
                "embedding_model":
                    settings.EMBEDDING_MODEL_NAME,
            }

            enriched_chunks.append(
                enriched_chunk
            )

        return enriched_chunks