"""
file: metadata.py
"""

from pathlib import Path
import re


def extract_document_metadata(
    source_file: str,
    text: str,
) -> dict:

    filename = Path(source_file).stem

    title = filename.replace("_", " ").title()
    document_name = filename
    publication_date = None

    date_match = re.search(
        r"\b(20\d{2}-\d{2}-\d{2})\b",
        text,
    )

    if date_match:
        publication_date = date_match.group(1)

    issuing_authority = "European Union"

    return {
        "document_id": filename.lower(),
        "document_number": filename,
        "regulation_title": title,
        "issuing_authority": issuing_authority,
        "publication_date": publication_date,
        "source_file": source_file,
    }