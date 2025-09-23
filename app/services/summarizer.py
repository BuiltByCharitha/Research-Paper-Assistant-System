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

# ---- Global Query (across all uploaded papers or general AI) ----
def global_query(query: str, k: int = 5, model: str = "llama3.2:1b", use_papers: bool = True) -> str:
    """
    Handles global queries:
      - If use_papers=True: run RAG across ALL uploaded papers.
      - If use_papers=False: use general LLM knowledge (no RAG).
    """
    if model not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported model: {model}. Choose from {SUPPORTED_MODELS}")

    if not use_papers:
        return ask_ollama(
            f"Answer this query with your general knowledge:\n\n{query}",
            model=model
        )

    # ---- RAG over all papers ----
    from services.embedder import STORAGE_DIR, load_paper_index
    import os

    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = encoder.encode([query], convert_to_numpy=True).astype(np.float32)

    all_chunks = []
    all_embeddings = []

    # Collect chunks from ALL uploaded papers
    if os.path.exists(STORAGE_DIR):
        for pid in os.listdir(STORAGE_DIR):
            try:
                index, chunks = load_paper_index(pid)
                if chunks:
                    all_chunks.extend(chunks)

                    # Recompute embeddings for all chunks (keeps it simple)
                    chunk_embeddings = encoder.encode(chunks, convert_to_numpy=True).astype(np.float32)
                    all_embeddings.append(chunk_embeddings)
            except Exception:
                continue

    if not all_chunks:
        return "No papers available for contextual search."

    # Stack all embeddings and build temporary FAISS index
    all_embeddings = np.vstack(all_embeddings)
    dim = all_embeddings.shape[1]
    temp_index = faiss.IndexFlatL2(dim)
    temp_index.add(all_embeddings)

    # Search
    D, I = temp_index.search(query_embedding, k)
    retrieved_chunks = [all_chunks[i] for i in I[0] if i < len(all_chunks)]
    combined_chunks = "\n".join(retrieved_chunks)

    # Prompt with context
    prompt = (
        f"Based on the following extracted parts from multiple research papers, "
        f"answer the query:\n\n{combined_chunks}\n\n"
        f"Query: {query}\n\nAnswer concisely:"
    )

    return ask_ollama(prompt, model=model)


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
