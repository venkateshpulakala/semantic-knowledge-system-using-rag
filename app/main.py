from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from collections import defaultdict

import os
import shutil
import traceback
import pickle

from app.ingestion import extract_text
from app.chunking import create_chunks
from app.embeddings import generate_embeddings
from app.vector_store import (
    add_to_vector_store,
    delete_document_from_vector_store
)
from app.retrieval import retrieve_documents
from app.generation import generate_answer


# ============================================
# 1. PROJECT DIRECTORIES
# ============================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

UPLOAD_DIR = os.path.join(BASE_DIR, "documents")

VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)


# ============================================
# 2. FASTAPI APPLICATION
# ============================================

app = FastAPI(
    title="Semantic Knowledge System using RAG",
    description="A document-based question answering system",
    version="1.0"
)


# Serve frontend files

app.mount(
    "/css",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")),
    name="css"
)

app.mount(
    "/js",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")),
    name="js"
)


# ============================================
# 3. REQUEST MODEL
# ============================================

class QuestionRequest(BaseModel):

    question: str


# ============================================
# 4. HOME PAGE
# ============================================

@app.get("/")
def home():

    return FileResponse(
        os.path.join(FRONTEND_DIR, "index.html")
    )


# ============================================
# 5. UPLOAD DOCUMENT
# ============================================

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    try:

        # Save PDF
        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(file.file, buffer)

        # Extract text
        extracted_pages = extract_text(file_path)

        if not extracted_pages:

            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF."
            )

        # Create chunks
        chunks = create_chunks(
            extracted_pages,
            file.filename
        )

        if not chunks:

            raise HTTPException(
                status_code=400,
                detail="No text chunks generated."
            )

        # Generate embeddings
        embeddings = generate_embeddings(chunks)

        # Add to existing vector database
        add_to_vector_store(
            embeddings,
            chunks
        )

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


# ============================================
# 6. GET ALL DOCUMENTS
# ============================================

@app.get("/documents")
def get_documents():

    try:

        documents = []

        document_data = defaultdict(
            lambda: {
                "pages": set(),
                "total_chunks": 0
            }
        )

        metadata_path = os.path.join(
            VECTOR_DB_DIR,
            "chunks.pkl"
        )

        # Read vector database metadata
        if os.path.exists(metadata_path):

            with open(metadata_path, "rb") as file:

                chunks = pickle.load(file)

            for chunk in chunks:

                metadata = chunk["metadata"]

                filename = metadata["source"]

                page = metadata["page"]

                document_data[filename]["pages"].add(page)

                document_data[filename]["total_chunks"] += 1

        # Read uploaded PDF files
        for filename in os.listdir(UPLOAD_DIR):

            file_path = os.path.join(
                UPLOAD_DIR,
                filename
            )

            if (
                os.path.isfile(file_path)
                and filename.lower().endswith(".pdf")
            ):

                info = document_data.get(
                    filename,
                    {
                        "pages": set(),
                        "total_chunks": 0
                    }
                )

                documents.append({

                    "filename": filename,

                    "total_pages": len(info["pages"]),

                    "total_chunks": info["total_chunks"]

                })

        return {
            "total_documents": len(documents),
            "documents": documents
        }

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.delete("/documents/{filename}")
def delete_document(filename: str):

    try:
        # Validate filename
        if filename != os.path.basename(filename) or filename in ("", ".", ".."):
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )

        # Get PDF path
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Check whether document exists
        if not os.path.isfile(file_path) or not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

        # Delete chunks and embeddings from FAISS
        deleted_chunks = delete_document_from_vector_store(filename)

        # Delete original PDF
        os.remove(file_path)

        return {
            "message": "Document deleted successfully",
            "filename": filename,
            "deleted_chunks": deleted_chunks
        }

    except HTTPException:
        raise

    except Exception as e:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================
# 7. ASK QUESTION
# ============================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    try:

        if not request.question.strip():

            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty."
            )

        # Retrieve relevant chunks
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

        # Extract unique sources
        sources = []

        seen_sources = set()

        for doc in retrieved_docs:

            source = doc["metadata"]["source"]

            page = doc["metadata"]["page"]

            source_key = (source, page)

            if source_key not in seen_sources:

                sources.append({
                    "document": source,
                    "page": page
                })

                seen_sources.add(source_key)

        return {
            "question": request.question,
            "answer": answer,
            "sources": sources
        }

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

