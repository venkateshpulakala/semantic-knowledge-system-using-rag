from app.embeddings import generate_query_embedding
from app.vector_store import load_vector_store


def retrieve_documents(question, top_k=5, min_score = 0.35):

    # 1. Validate the question
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    # 2. Load FAISS index and stored chunks
    index, chunks = load_vector_store()

    # 3. Check whether the database contains vectors
    if index.ntotal == 0:
        return []

    # 4. Generate embedding for user question
    query_embedding = generate_query_embedding(question)

    # 5. Limit the number of search results
    top_k = min(top_k, index.ntotal)

    # 6. Search for similar vectors
    scores, indices = index.search(query_embedding, top_k)

    retrieved_chunks = []

    # 7. Check relevance using similarity threshold
    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        if score < min_score:
            continue

        retrieved_chunks.append({

            "text": chunks[idx]["text"],

            "metadata": chunks[idx]["metadata"],

            "score": float(score)

        })

    # 8. Return retrieved results
    return retrieved_chunks