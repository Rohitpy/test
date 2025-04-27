LangChain (v0.2.5) & LangChain-community (v0.2.5)

Framework for building RAG applications
Provides components for document loading, text splitting, embeddings, and vector stores
Helps orchestrate the interaction between documents and LLMs
OpenAI (v1.35.7)

Integration with OpenAI's models for completion and embeddings
Used for generating responses and creating embeddings for vector search
Document Processing Stack
Unstructured (v0.11.8)

Handles document parsing from various formats
Extracts clean text from PDFs, images, and other document types
PyMuPDF/Fitz (v1.23.26)

Advanced PDF processing
Extracts text, images, and maintains document structure
Tesseract (v0.1.3)

OCR capabilities for extracting text from images
Critical for handling scanned documents
Vector Storage & Search
FAISS-cpu (v1.8.0)
Efficient similarity search and clustering of dense vectors
Used for storing and retrieving document embeddings
API Framework
FastAPI (v0.111.0) & Pydantic (v2.7.4)
Modern web framework for building the chatbot API
Data validation and settings management
Handles HTTP requests and responses
Text Processing & Embeddings
Sentence-transformers (v2.2.2)

Creates dense vector embeddings for text
Powers semantic search capabilities
Spacy (v3.7.4)

NLP tasks like tokenization and text preprocessing
Helps in text cleaning and analysis
Database & Storage
SQLAlchemy (v1.4.52)
ORM for database operations
Stores conversation history and document metadata
This stack creates a robust RAG system where documents are
