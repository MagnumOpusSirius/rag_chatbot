import os
import re
import json
import pdfplumber
from tqdm import tqdm
from pathlib import Path

RAW_PDF_DIR = Path("data/raw_pdfs")
OUTPUT_JSON_DIR = Path("data/processed_chunks_json")
OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)

# Regex patterns
HEADER_REGEX = re.compile(r"^\d+(\.\d+)*\s+.+")  # e.g., 2.1 Creating a Document
BULLET_REGEX = re.compile(r"^(\*|-|•|\d+\.)\s+.+")  # Detect bullets
FOOTER_NOISE = re.compile(r"(Page\s+\d+|Confidential|Company Name)", re.IGNORECASE)

def clean_text(text):
    """Remove empty lines and header/footer noise."""
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    cleaned_lines = [line for line in cleaned_lines if not FOOTER_NOISE.search(line)]
    return cleaned_lines

def chunk_by_section(lines, filename, page):
    chunks = []
    current_section = {"section": "Introduction", "content": []}

    for line in lines:
        if HEADER_REGEX.match(line):
            # Save previous chunk
            if current_section["content"]:
                chunks.append({
                    "source": filename,
                    "section": current_section["section"],
                    "content": "\n".join(current_section["content"]),
                    "metadata": {"page": page, "filename": filename}
                })
            current_section = {"section": line, "content": []}
        else:
            current_section["content"].append(line)

    # Save last chunk
    if current_section["content"]:
        chunks.append({
            "source": filename,
            "section": current_section["section"],
            "content": "\n".join(current_section["content"]),
            "metadata": {"page": page, "filename": filename}
        })
    return chunks

def process_pdf(pdf_path):
    all_chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            lines = clean_text(text)
            chunks = chunk_by_section(lines, pdf_path.name, page=i+1)
            all_chunks.extend(chunks)
    return all_chunks

def main():
    pdf_files = list(RAW_PDF_DIR.glob("*.pdf"))

    for pdf_file in tqdm(pdf_files, desc="Chunking PDFs"):
        chunks = process_pdf(pdf_file)
        out_path = OUTPUT_JSON_DIR / f"{pdf_file.stem}_chunks.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Chunking complete. JSON files saved in {OUTPUT_JSON_DIR}")

if __name__ == "__main__":
    main()