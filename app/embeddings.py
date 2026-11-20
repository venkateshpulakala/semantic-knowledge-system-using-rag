from sentence_transformers import SentenceTransformer

import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def generate_embeddings(chunks):

    if not chunks:
        return np.empty((0,384), dtype = np.float32)

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy = True,
        normalize_embeddings = True,
        show_progress_bar = True
    )

    return np.asarray(embeddings, dtype = np.float32)

def generate_query_embedding(question):

    embedding = model.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return np.asarray([embedding], dtype=np.float32)