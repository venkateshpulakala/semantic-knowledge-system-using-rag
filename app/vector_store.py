import faiss
import numpy as np
import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

os.makedirs(VECTOR_DB_DIR, exist_ok = True)


#file paths
INDEX_PATH = os.path.join(VECTOR_DB_DIR,"index.faiss")

METADATA_PATH = os.path.join(VECTOR_DB_DIR, "chunks.pkl")

#Embedding dimensions
EMBEDDING_DIMENSION = 384

#Create and save a new vector database
def create_vector_store(embeddings, chunks):

    embeddings = np.asarray(embeddings, dtype = np.float32)
    faiss.normalize_L2(embeddings)

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array")

    if embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError("Invalid embedding dimensions")

    if len(embeddings) != len(chunks):
        raise ValueError("No embeddings provided")

    #Create FAISS INDEX
    index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

    #Add embeddings to index
    index.add(embeddings)

    #save index and chunks
    save_vector_store(index, chunks)

    return index

def save_vector_store(index, chunks):

    if index.ntotal != len(chunks):
        raise ValueError("Index and chunk count do not match")

    faiss.write_index(index, INDEX_PATH)

    with open(METADATA_PATH, "wb") as file:
        pickle.dump(chunks, file)

def load_vector_store():

    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("FAISS  index not found")

    if not os.path.exists(METADATA_PATH):
        raise FileNotFoundError("chunk metadata not found")

    # Load FAISS INDEX
    index = faiss.read_index(INDEX_PATH)

    # Load original chunks and metadata
    with open(METADATA_PATH, "rb") as file:
        chunks = pickle.load(file)

    if index.ntotal != len(chunks):
        raise ValueError("Index and metadata are inconsistend")

    return index, chunks

# Add new documents to existing vector database
def add_to_vector_store(embeddings, new_chunks):

    embeddings = np.asarray(embeddings, dtype = np.float32)

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2d array")

    if embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError("Invalid embedding dimensions")

    if len(embeddings) != len(new_chunks):
        raise ValueError("Number of embeddings and chunks must match")

    if len(embeddings) == 0:
        return

    # Load existing database if available
    if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):

        index, chunks = load_vector_store()
    else:
        index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

        chunks = []

    # Add new embeddings
    index.add(embeddings)

    # Add correspoding chunk metadata
    chunks.extend(new_chunks)

    # Save and update database
    save_vector_store(index, chunks)

    return index