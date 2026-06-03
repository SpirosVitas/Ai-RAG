"""
Μην τρεξετε τον κωδικα γιατι τα κατεβασα τα αρχεια στον φακελο eu_docs 
και επρεπε να τα κατεβαζω σιγα σιγα για να μην μας banarei το eurlex
οποιος τα παρει για chuncking εχει ετοιμα τα αρχεια. 
"""

import requests
from pathlib import Path
import time

def download_eurlex_pdf_by_celex(celex_id: str, language: str = "EN", out_dir: str = "eu_docs"):
    """
    Download an official legal PDF document from EUR-Lex using the CELEX ID.
    """
    # Create the output directory if it does not exist
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # Construct the target EUR-Lex URL
    url = (
        "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/"
        f"?uri=CELEX:{celex_id}&from={language}"
    )
    print(f"Starting download from: {url}")

    headers = {
        "User-Agent": "Python EUR-Lex downloader/1.0"
    }

    # Execute request with a 60-second timeout to handle slow EU servers
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()

    # Validate if the returned file format is PDF
    content_type = response.headers.get("Content-Type", "")
    if "pdf" not in content_type.lower():
        print(f"Warning: File for CELEX {celex_id} might not be a valid PDF (Content-Type: {content_type})")

    # Define local file path destination
    file_path = Path(out_dir) / f"{celex_id}_{language}.pdf"
    
    # Write response binary content to local file
    file_path.write_bytes(response.content)

    return file_path


if __name__ == "__main__":
    print("Starting Ingestion Pipeline for the 5 core Financial Compliance regulations...")
    print("-" * 80)

    # Targeted list of the 5 core compliance regulations
    list_of_celexs = [
        "32022R2554",  # DORA Regulation
        "32018L0843",  # AMLD 5 Directive
        "32014L0065",  # MiFID II Directive
        "32016R0679",  # GDPR Regulation
        "32024R1689"   # AI Act Regulation
    ]
    
    for idx, celex in enumerate(list_of_celexs, 1):
        try:
            print(f"\n [{idx}/{len(list_of_celexs)}] Processing CELEX: {celex}")
            path = download_eurlex_pdf_by_celex(celex, language="EN")
            print(f" File successfully saved to: {path}")
            
            # Rate limiting mitigation strategy
            if idx < len(list_of_celexs):  # Skip delay for the final file execution
                print(" Waiting 3 seconds to protect the EUR-Lex API endpoint...")
                time.sleep(3)
            
        except Exception as e:
            print(f" Failed to download document for CELEX {celex}: {e}")

    print("\n" + "=" * 80)
    print(" Process completed. Please check the 'eu_docs' directory for the downloaded files.")
    print("=" * 80)