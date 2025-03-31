import os
import json
import fitz  # PyMuPDF for PDF text extraction
import faiss
import numpy as np
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = "embeddings/chunks.json"
FAISS_INDEX_FILE = "embeddings/faiss_index.bin"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Splits text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return text_splitter.split_text(text)

def load_existing_chunks() -> List[str]:
    """Loads existing chunks from JSON."""
    if os.path.exists(CHUNKS_FILE):
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chunks(new_chunks: List[str]):
    """Appends new chunks to the JSON file."""
    chunks = load_existing_chunks()
    chunks.extend(new_chunks)

    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)

def embed_text(chunks: List[str]):
    """Embeds text chunks using SentenceTransformer and stores in FAISS."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, convert_to_numpy=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_FILE)
    print("Embeddings stored in FAISS.")

def update_embeddings(pdf_path: str):
    """Processes a new PDF, extracts text, chunks it, and updates embeddings."""
    print(f"Processing PDF: {pdf_path}...")
    
    text = extract_text_from_pdf(pdf_path)
    new_chunks = chunk_text(text)
    
    if not new_chunks:
        print("No text extracted. Make sure the PDF has readable text.")
        return

    save_chunks(new_chunks)  # Save to JSON
    embed_text(load_existing_chunks())  # Embed all chunks

    print("PDF processed and embeddings updated!")

def retrieve_similar(query: str, top_k: int = 3):
    """Retrieves the top_k most similar text chunks to a given query."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode([query], convert_to_numpy=True)

    if not os.path.exists(FAISS_INDEX_FILE):
        print("FAISS index not found. Run embedding first.")
        return

    index = faiss.read_index(FAISS_INDEX_FILE)
    distances, indices = index.search(query_embedding, top_k)

    chunks = load_existing_chunks()

    print("Top similar chunks:")
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks):
            print(f"Rank {i+1}: {chunks[idx]} (Distance: {distances[0][i]})")

if __name__ == "__main__":
    pdf_file = "data/cons.pdf"  # Replace with actual file path
    
    if os.path.exists(pdf_file):
        update_embeddings(pdf_file)
    else:
        print("No PDF file found.")
