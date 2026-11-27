# Semantic Knowledge System Using RAG

## 1. Project Overview

The **Semantic Knowledge System using Retrieval-Augmented Generation (RAG)** is an intelligent document-based question-answering application that allows users to upload PDF documents and ask questions based on their content.

The system retrieves relevant information from uploaded documents using semantic search and generates accurate, context-based answers using a Large Language Model (LLM).

Unlike general AI chatbots, this system focuses on answering questions using the information available in the uploaded documents.

## 2. Objectives

- Develop an intelligent document-based question-answering system using RAG.
- Extract meaningful information from PDF documents.
- Retrieve relevant content using semantic similarity.
- Generate context-aware answers using Large Language Models.
- Provide a simple interface for uploading, managing, and querying documents.

## 3. Key Features

- **PDF Upload:** Upload PDF documents through the web interface.
- **Text Extraction:** Extract text from PDF documents.
- **Text Chunking:** Divide extracted text into smaller chunks for efficient processing.
- **Embedding Generation:** Convert text chunks into numerical vector representations.
- **Vector Storage:** Store embeddings using FAISS.
- **Semantic Search:** Retrieve relevant document sections based on user queries.
- **AI-Powered Answers:** Generate answers using Groq LLM based on retrieved context.
- **Document Management:** View and delete uploaded PDF documents.
- **Context-Based Responses:** Generate answers using the uploaded document content rather than relying on unrelated external information.

## 4. Technologies Used

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Frontend | HTML, CSS, JavaScript |
| PDF Text Extraction | PyMuPDF |
| Text Chunking | LangChain |
| Embedding Model | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector Database | FAISS |
| Large Language Model | Groq |
| API Testing | Swagger UI |
| Version Control | Git and GitHub |

## 5. System Architecture

The project follows a Retrieval-Augmented Generation (RAG) architecture.

### Document Processing Pipeline

1. User uploads a PDF document.
2. FastAPI receives the uploaded document.
3. PyMuPDF extracts text from the PDF.
4. LangChain splits the extracted text into smaller chunks.
5. Sentence Transformers generates embeddings for each chunk.
6. FAISS stores the embeddings for efficient similarity search.

### Question Answering Pipeline

1. User enters a question through the frontend.
2. The question is converted into an embedding.
3. FAISS retrieves the most relevant document chunks.
4. Retrieved content is passed to the Groq LLM.
5. The LLM generates an answer based on the retrieved context.
6. The answer is displayed in the frontend.

## 6. Project Structure

```text
Semantic-Knowledge-System-Using-RAG/
│
├── app/
│   ├── main.py
│   ├── ingestion.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retrieval.py
│   └── generation.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── documents/
├── vector_db/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 7. Installation and Setup

### Prerequisites

- Python 3.10 or above
- Git
- Groq API Key

### Step 1: Clone the Repository

```bash
git clone https://github.com/venkateshpulakala/sematic_knowledge_system_using_rag.git
```

### Step 2: Navigate to the Project Directory

```bash
cd sematic_knowledge_system_using_rag
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Create a `.env` file in the project root directory.

Add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

Replace `your_groq_api_key` with your actual API key.

**Important:** Never upload your `.env` file or API key to GitHub.

### Step 6: Run the Application

```bash
uvicorn app.main:app --reload
```

### Step 7: Open the Application

Frontend:

```text
http://127.0.0.1:8000/
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

## 8. How to Use

1. Start the application.
2. Open the frontend in your browser.
3. Upload a PDF document.
4. Wait for document processing to complete.
5. View uploaded documents in the document section.
6. Enter a question related to the uploaded document.
7. Receive an AI-generated answer based on the document content.
8. Delete documents when they are no longer required.

## 9. Future Enhancements

- Document-specific question answering.
- Support for multiple file formats such as DOCX, TXT, and PPTX.
- Advanced document filtering and search.
- Chat history and conversation memory.
- Source citations with page numbers.
- Improved retrieval accuracy using reranking.
- User authentication and personalized document management.
- Cloud deployment.

## 10. Learning Outcomes

- Understanding Retrieval-Augmented Generation architecture.
- Working with Large Language Models.
- Implementing semantic search using vector embeddings.
- Understanding vector databases and similarity search.
- Building REST APIs using FastAPI.
- Integrating frontend and backend components.
- Developing an end-to-end AI-powered application.

## 11. Author

**Venkatesh Pulakala**

GitHub: https://github.com/venkateshpulakala

---

*This project demonstrates the practical implementation of Retrieval-Augmented Generation for intelligent document understanding and question answering.*