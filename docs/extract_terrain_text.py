#!/usr/bin/env python3
import pdfplumber
from pathlib import Path

PDF_NAME = "papiers-terrain.pdf"   # <- nom corrigé
OUTPUT_NAME = "terrain-transcription.txt"

def main():
    base_dir = Path(__file__).resolve().parent
    pdf_path = base_dir / PDF_NAME
    out_path = base_dir / OUTPUT_NAME

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf, out_path.open("w", encoding="utf-8") as f:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            f.write(f"\n--- PAGINA {i} ---\n")
            f.write(text)
            f.write("\n")

    print(f"Transcription saved to: {out_path}")

if __name__ == "__main__":
    main()
