import os
import re
import json
import pdfplumber
from tqdm import tqdm
from pathlib import Path

RAW_PDF_DIR = Path("data/raw_pdfs")
OUTPUT_JSONL_FILE = Path("data/chunked_output.jsonl")
OUTPUT_JSONL_FILE.parent.mkdir(parents=True, exist_ok=True)

# Regex patterns
HEADER_REGEX = re.compile(r"^\d+(\.\d+)*\s+.+")  # e.g., 2.1 Creating a Document
FOOTER_NOISE = re.compile(r"(Page\s+\d+|Confidential|Company Name)", re.IGNORECASE)

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
            if current_section["content"]:
                chunks.append({
                    "source": filename,
                    "section": current_section["section"],
                    "content": "\n".join(current_section["content"]),
                    "metadata": {"page": page, "filename": filename}
                })
            current_section = {"section": line.strip(), "content": []}
        else:
            current_section["content"].append(line.strip())

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

    with open(OUTPUT_JSONL_FILE, "w", encoding="utf-8") as f_out:
        for pdf_file in tqdm(pdf_files, desc="Chunking PDFs"):
            chunks = process_pdf(pdf_file)
            for chunk in chunks:
                f_out.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"\n✅ Section-aware chunking complete. Data saved to {OUTPUT_JSONL_FILE}")

if __name__ == "__main__":
    main()
