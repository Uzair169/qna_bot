import json
import faiss
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import numpy as np

app = Flask(__name__)

# Load FAISS index
index = faiss.read_index("embeddings/faiss_index.bin")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load text chunks from JSON
with open("embeddings/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

def retrieve_similar(query: str, top_k: int = 3):
    """Retrieves the top_k most similar text chunks to a given query."""
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        chunk_text = chunks[int(idx)]  # Retrieve actual chunk text
        results.append({
            "rank": i + 1,
            "text": chunk_text,
            "distance": float(distances[0][i])
        })
    
    return results

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running", "endpoints": ["/search"]})


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()
    top_k = int(request.args.get("top_k", 3))

    if not query:
        return jsonify({"error": "Query parameter is required", "results": []}), 400

    try:
        results = retrieve_similar(query, top_k)
        return jsonify({"query": query, "results": results})
    except Exception as e:
        return jsonify({"error": str(e), "results": []}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
