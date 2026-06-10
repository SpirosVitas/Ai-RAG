"""
file: chunking.py

Structure-aware chunking for regulatory documents.

Strategy:
1. Split document into Articles when possible.
2. Apply RecursiveCharacterTextSplitter inside each Article.
3. Generate chunk metadata suitable for RAG retrieval.
Structure-aware chunking for regulatory documents.

Pipeline:
PDF Pages
    ↓
Merge Pages
    ↓
Split by Articles
    ↓
Recursive Chunking
    ↓
Chunk Records
"""

from hashlib import sha256
import re
from src.config.settings import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.ingestion.metadata import extract_document_metadata


ARTICLE_PATTERN = re.compile(
    r"(Article\s+\d+[A-Za-z\-]*.*?)"
    r"(?=(?:Article\s+\d+[A-Za-z\-]*)|$)",
    re.DOTALL | re.IGNORECASE,
)

def merge_pages(pages: list[dict]) -> dict:
    """
    Merge all pages belonging to a document.

    Expected page format:
    {
        "source_file": "...",
        "page_number": 1,
        "text": "..."
    }
    """

    if not pages:
        raise ValueError("No pages provided")
    pages = sorted(
        pages,
        key=lambda p: p["page_number"],
    )

    merged_text = "\n\n".join(
        page["text"]
        for page in pages
        if page["text"].strip()
    )

    return {
        "source_file": pages[0]["source_file"],
        "total_pages": len(pages),
        "text": merged_text,
    }


def split_by_articles(text: str) -> list[tuple[str, str]]:
    """
    Split documents into articles
    Returns:
        [
            ("Article 1", "<article text>"),
            ("Article 2", "<article text>")
        ]
    """

    matches = ARTICLE_PATTERN.findall(text)

    if not matches:
        return [("Unknown", text)]

    articles = []
#    articles: list[tuple[str, str]] = []

    for article_text in matches:
        header_match = re.search(
            r"Article\s+\d+[A-Za-z\-]*",
            article_text,
            flags=re.IGNORECASE,
        )

        article_reference = (
            header_match.group(0)
            if header_match
            else "Unknown"
        )

        articles.append((article_reference, article_text.strip()))

    return articles


def recursive_chunk(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "; ",
            " ",
            "",
        ],
    )

    return splitter.split_text(text)



def create_chunks(
    pages: list[dict],
) -> list[dict]:
    """
    Create chunks from a complete PDF.

    Parameters
    ----------
    pages:
        List of extracted PDF pages.

    Returns
    -------
    List[dict]
        Chunk records ready for embeddings.
    """

    document = merge_pages(pages)

    source_file = document["source_file"]
    document_metadata = extract_document_metadata(
    source_file=source_file,
    text=document["text"],
)

    articles = split_by_articles(
        document["text"]
    )

    chunk_rows = []

    global_chunk_index = 0

    for article_reference, article_text in articles:

        chunks = recursive_chunk(
            text=article_text,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP,
        )

        for article_chunk_index, chunk in enumerate(chunks):

            chunk_id = sha256(
                (
                    f"{source_file}|"
                    f"{article_reference}|"
                    f"{article_chunk_index}|"
                    f"{chunk}"
                ).encode("utf-8")
            ).hexdigest()

            chunk_rows.append(
                {
                    "chunk_id": chunk_id,
                    **document_metadata,
                    "source_file": source_file,
                    "document_name": source_file,
                    "article_reference": article_reference,
                    "chunk_index": global_chunk_index,
                    "article_chunk_index": article_chunk_index,
                    "content": chunk,
                }
            )

            global_chunk_index += 1

    print(
    f"{source_file}: {len(chunks)} chunks")
    return chunk_rows