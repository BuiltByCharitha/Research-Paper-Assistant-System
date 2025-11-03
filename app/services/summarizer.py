import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama

from services.embedder import load_paper_index

# Supported models (lightweight options)
SUPPORTED_MODELS = ["llama3.2:1b", "phi3:mini", "gemma:2b"]

# ---- Ask Ollama ----
def ask_ollama(prompt: str, model: str = "llama3.2:1b") -> str:
    if model not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported model: {model}. Choose from {SUPPORTED_MODELS}")

    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# ---- Full paper summarization ----
def summarize_full_paper(paper_id: str, model: str = "llama3.2:1b") -> str:
    index, chunks = load_paper_index(paper_id)

    if not chunks:
        return "No content found for this paper."

    # Summarize each chunk separately
    chunk_summaries = [
        ask_ollama(f"Summarize this part of a research paper:\n\n{chunk}", model=model)
        for chunk in chunks
    ]

    # Combine and generate final concise summary
    combined = " ".join(chunk_summaries)
    final_summary = ask_ollama(
        f"Provide a concise, coherent summary of this research paper based on the following:\n\n{combined}",
        model=model,
    )
    return final_summary

# ---- Query-based summarization ----
def summarize_query(paper_id: str, query: str, k: int = 3, model: str = "llama3.2:1b") -> str:
    index, chunks = load_paper_index(paper_id)

    if not chunks:
        return "No content found for this paper."

    # Encode query
    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = encoder.encode([query], convert_to_numpy=True).astype(np.float32)

    # Search in FAISS
    D, I = index.search(query_embedding, k)
    retrieved_chunks = [chunks[i] for i in I[0] if i < len(chunks)]
    combined_chunks = "\n".join(retrieved_chunks)

    # Build prompt
    prompt = (
        f"Based on the following extracted parts of a research paper, answer the query:\n\n"
        f"{combined_chunks}\n\n"
        f"Query: {query}\n\nAnswer concisely:"
    )

    return ask_ollama(prompt, model=model)
