import faiss
import numpy as np
import pickle
import os

from app.embeddings import generate_embeddings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

os.makedirs(VECTOR_DB_DIR, exist_ok=True)


# File paths
INDEX_PATH = os.path.join(VECTOR_DB_DIR, "index.faiss")

METADATA_PATH = os.path.join(VECTOR_DB_DIR, "chunks.pkl")


# Embedding dimensions
EMBEDDING_DIMENSION = 384


# Create and save a new vector database
def create_vector_store(embeddings, chunks):

    embeddings = np.asarray(embeddings, dtype=np.float32)

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array")

    if embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError("Invalid embedding dimensions")

    if len(embeddings) != len(chunks):
        raise ValueError("Number of embeddings and chunks must match")

    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

    index.add(embeddings)

    save_vector_store(index, chunks)

    return index


# Save vector database
def save_vector_store(index, chunks):

    if index.ntotal != len(chunks):
        raise ValueError("Index and chunk count do not match")

    faiss.write_index(index, INDEX_PATH)

    with open(METADATA_PATH, "wb") as file:
        pickle.dump(chunks, file)


# Load vector database
def load_vector_store():

    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("FAISS index not found")

    if not os.path.exists(METADATA_PATH):
        raise FileNotFoundError("Chunk metadata not found")

    index = faiss.read_index(INDEX_PATH)

    with open(METADATA_PATH, "rb") as file:
        chunks = pickle.load(file)

    if index.ntotal != len(chunks):
        raise ValueError("Index and metadata are inconsistent")

    return index, chunks


# Add new documents to existing vector database
def add_to_vector_store(embeddings, new_chunks):

    embeddings = np.asarray(embeddings, dtype=np.float32)

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array")

    if embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError("Invalid embedding dimensions")

    if len(embeddings) != len(new_chunks):
        raise ValueError("Number of embeddings and chunks must match")

    if len(embeddings) == 0:
        return

    faiss.normalize_L2(embeddings)

    if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):

        index, chunks = load_vector_store()

    else:

        index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

        chunks = []

    index.add(embeddings)

    chunks.extend(new_chunks)

    save_vector_store(index, chunks)

    return index


# Delete document from vector database
def delete_document_from_vector_store(filename):

    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):

        return 0

    index, chunks = load_vector_store()

    # Keep chunks belonging to other documents
    remaining_chunks = [
        chunk for chunk in chunks
        if chunk["metadata"]["source"] != filename
    ]

    deleted_count = len(chunks) - len(remaining_chunks)

    if deleted_count == 0:
        return 0

    # If no chunks remain, remove vector database files
    if not remaining_chunks:

        os.remove(INDEX_PATH)
        os.remove(METADATA_PATH)

        return deleted_count

    # Generate embeddings for remaining chunks
    remaining_embeddings = generate_embeddings(remaining_chunks)

    remaining_embeddings = np.asarray(
        remaining_embeddings,
        dtype=np.float32
    )

    if remaining_embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array")

    if remaining_embeddings.shape != (
        len(remaining_chunks),
        EMBEDDING_DIMENSION
    ):
        raise ValueError("Invalid remaining embedding dimensions")

    faiss.normalize_L2(remaining_embeddings)

    # Create a fresh FAISS index
    new_index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

    new_index.add(remaining_embeddings)

    # Save updated database
    save_vector_store(new_index, remaining_chunks)

    return deleted_count