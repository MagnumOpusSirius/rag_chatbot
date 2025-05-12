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

# Known legal/footer boilerplate phrases to remove
NOISE_PHRASES = [
    "use and copying of any intelinotion software described in this publication requires an applicable software license",
    "intelinotion believes the information in this publication is accurate as of its publication date",
    "the information is subject to change",
    "without notice",
    "shared without prior written consent of intelinotion llc",
    "422 executive drive, building 4, princeton, nj, 08540 info@intelinotion.com page"
]

def is_noise_line(line):
    normalized = line.lower().strip()
    return any(noise in normalized for noise in NOISE_PHRASES)

def clean_text(text):
    """Remove empty lines, footer patterns, and known noise phrases."""
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if FOOTER_NOISE.search(stripped):
            continue
        if is_noise_line(stripped):
            continue
        cleaned_lines.append(stripped)
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