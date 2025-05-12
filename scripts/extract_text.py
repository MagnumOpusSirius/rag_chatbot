import os
import pdfplumber
from pathlib import Path
from tqdm import tqdm

RAW_PDF_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("data/processed_chunks")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = list(RAW_PDF_DIR.glob("*.pdf"))

    for pdf_file in tqdm(pdf_files, desc="Extracting text"):
        text = extract_text_from_pdf(pdf_file)
        output_file = OUTPUT_DIR / f"{pdf_file.stem}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

    print(f"\n✅ Extraction complete. Text files saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()