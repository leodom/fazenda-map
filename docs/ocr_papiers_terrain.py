#!/usr/bin/env python3
from pathlib import Path

from pdf2image import convert_from_path
import pytesseract

PDF_NAME = "papiers-terrain.pdf"
OUTPUT_NAME = "papiers-terrain-ocr.txt"
LANG = "por"   # modèle portugais de Tesseract

def main():
    base_dir = Path(__file__).resolve().parent
    pdf_path = base_dir / PDF_NAME
    out_path = base_dir / OUTPUT_NAME

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # conversion PDF -> liste d’images (une par page)
    images = convert_from_path(str(pdf_path), dpi=300)

    with out_path.open("w", encoding="utf-8") as f:
        for i, img in enumerate(images, start=1):
            text = pytesseract.image_to_string(img, lang=LANG)
            f.write(f"\n--- PAGINA {i} ---\n")
            f.write(text)
            f.write("\n")

    print(f"OCR done, output: {out_path}")

if __name__ == "__main__":
    main()
