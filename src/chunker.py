import os
import json
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter

CHUNKS_FILE = "embeddings/chunks.json"

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    """Splits text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return text_splitter.split_text(text)

def save_chunks(new_chunks):
    """Appends new chunks to the existing chunks.json file."""
    if os.path.exists(CHUNKS_FILE):
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    else:
        chunks = []

    chunks.extend(new_chunks)

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)

def process_new_pdf(pdf_path):
    """Extracts text, chunks it, and saves the chunks."""
    text = extract_text_from_pdf(pdf_path)
    new_chunks = chunk_text(text)
    save_chunks(new_chunks)
    return new_chunks

if __name__ == "__main__":
    new_pdf = "data/cons.pdf"  # Replace with your actual PDF file path
    if os.path.exists(new_pdf):
        process_new_pdf(new_pdf)
        print("New PDF processed and chunks saved!")
    else:
        print("No new PDF file found.")
