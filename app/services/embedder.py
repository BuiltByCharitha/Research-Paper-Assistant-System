from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import json
from services.pdf_loader import extract_text, chunk_text

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

STORAGE_DIR:str = "storage"

def ensure_storage(paper_id: str):
    paper_dir = os.path.join(STORAGE_DIR, paper_id)
    os.makedirs(paper_dir, exist_ok=True)
    return paper_dir

def create_index_for_paper(paper_id: str, text_chunks):
    """Create FAISS index + store chunks and metadata for a specific paper"""
    paper_dir = ensure_storage(paper_id)
    dim = 384
    index = faiss.IndexFlatL2(dim)

    # Add embeddings
    embeddings = model.encode(text_chunks, convert_to_tensor=False)
    index.add(np.array(embeddings, dtype=np.float32))

    # Save index and chunks
    faiss.write_index(index, os.path.join(paper_dir, "faiss_index.bin"))
    with open(os.path.join(paper_dir, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(text_chunks, f)

    # --- Extract title ---
    title = text_chunks[0][:200] if text_chunks else "Untitled"
    metadata = {
        "paper_id": paper_id,
        "num_chunks": len(text_chunks),
        "title": title or "Untitled Paper"
    }
    with open(os.path.join(paper_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f)

    return metadata

def load_paper_index(paper_id: str):
    """Load FAISS index + chunks for a paper"""
    paper_dir = ensure_storage(paper_id)
    index = faiss.read_index(os.path.join(paper_dir, "faiss_index.bin"))
    with open(os.path.join(paper_dir, "chunks.json"), "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks

