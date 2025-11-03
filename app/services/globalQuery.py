import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
from sqlalchemy.orm import Session

from services.embedder import load_paper_index
from services.database import User, Paper
from services.summarizer import SUPPORTED_MODELS, ask_ollama

# ---- Global Query (across all uploaded papers or general AI) ----
def global_query(
    query: str, 
    current_user: User,  
    db: Session,
    k: int = 5, 
    model: str = "llama3.2:1b", 
    use_papers: bool = True
) -> str:
    """
    Handles global queries:
      - If use_papers=True: run RAG across papers uploaded by the current user.
      - If use_papers=False: use general LLM knowledge (no RAG).
    """
    if model not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported model: {model}. Choose from {SUPPORTED_MODELS}")

    if not use_papers:
        return ask_ollama(
            f"Answer this query with your general knowledge:\n\n{query}",
            model=model
        )

    from services.embedder import load_paper_index
    import numpy as np
    import faiss

    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = encoder.encode([query], convert_to_numpy=True).astype(np.float32)

    all_chunks = []
    all_embeddings = []

    # Fetch papers for the current user from DB
    user_papers = db.query(Paper).filter(Paper.user_id == current_user.id).all()
    for paper in user_papers:
        try:
            index, chunks = load_paper_index(str(paper.id))
            if chunks:
                all_chunks.extend(chunks)
                chunk_embeddings = encoder.encode(chunks, convert_to_numpy=True).astype(np.float32)
                all_embeddings.append(chunk_embeddings)
        except Exception:
            continue

    if not all_chunks:
        return "No papers available for contextual search."

    # Stack embeddings and build temporary FAISS index
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
        f"Based on the following extracted parts from your uploaded research papers, "
        f"answer the query:\n\n{combined_chunks}\n\n"
        f"Query: {query}\n\nAnswer concisely:"
    )

    return ask_ollama(prompt, model=model)