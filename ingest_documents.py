from __future__ import annotations
import argparse
from pathlib import Path
from company_system.rag.ingest import ingest_pdf

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Kept for a simple setup interface; ingestion always rebuilds the policy collection.")
    args = parser.parse_args()
    pdf_path = Path("company_system/documents/company_handbook.pdf")
    print(ingest_pdf(pdf_path))
