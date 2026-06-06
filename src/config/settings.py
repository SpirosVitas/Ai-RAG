from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    VECTOR_DB_DIR: Path = (BASE_DIR / "data" / "vector_db")

#   DATA_DIR: Path = BASE_DIR / "data"

#    PDF_PATH: Path = (
#        DATA_DIR / "32016R0679_EN.pdf"
#    )
    DOCUMENTS_DIR: Path = BASE_DIR / "data" / "eu_docs"
    # Chunking
    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 250

    # Retrieval
    TOP_K: int = 5

    # Embeddings
    EMBEDDING_MODEL_NAME: str = ("sentence-transformers/all-MiniLM-L6-v2")
    #EMBEDDING_MODEL_NAME: str = ("text-embedding-3-large")

    # Vector Store
    COLLECTION_NAME: str = (
        "eu_regulations"
    )

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = Field(...)
    AZURE_OPENAI_API_KEY: str = Field(...)
    AZURE_OPENAI_API_VERSION: str = Field(...)
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(...)


settings = Settings()