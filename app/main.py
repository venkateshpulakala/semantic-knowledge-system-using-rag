from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import traceback

import os
import shutil

from app.ingestion import extract_text
from app.chunking import create_chunks
from app.embeddings import generate_embeddings
from app.vector_store import create_vector_store
from app.retrieval import retrieve_documents
from app.generation import generate_answer


app = FastAPI(
    title="Semantic Knowledge System using RAG",
    description="A document-based question answering system",
    version="1.0"
)


UPLOAD_DIR = "documents"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# Request model
class QuestionRequest(BaseModel):
    question: str


# Home endpoint
@app.get("/")
def home():

    return {
        "message": "Welcome to Semantic Knowledge System using RAG",
        "status": "Running"
    }


# Document upload endpoint
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:

        # Save uploaded PDF
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        extracted_pages = extract_text(file_path)

        # Create chunks
        chunks = create_chunks(
            extracted_pages,
            file.filename
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF."
            )

        # Generate embeddings
        embeddings = generate_embeddings(chunks)

        # Store vectors and metadata
        create_vector_store(embeddings, chunks)

        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "total_pages": len(extracted_pages),
            "total_chunks": len(chunks)
        }

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        await file.close()


# Question answering endpoint
@app.post("/ask")
def ask_question(request: QuestionRequest):

    try:

        # Retrieve relevant documents
        retrieved_docs = retrieve_documents(
            request.question,
            top_k=5,
            min_score=0.35
        )

        if not retrieved_docs:
            return {
                "question": request.question,
                "answer": "I couldn't find relevant information in your documents.",
                "sources": []
            }

        # Generate answer
        answer = generate_answer(
            request.question,
            retrieved_docs
        )

        # Extract source information
        sources = []

        for doc in retrieved_docs:

            sources.append({
                "source": doc["metadata"]["source"],
                "page": doc["metadata"]["page"]
            })

        return {
            "question": request.question,
            "answer": answer,
            "sources": sources
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )