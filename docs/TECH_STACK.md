# Technology Stack Specification

This document records the exact, verified technologies implemented across the Intelligent Bug Diagnosis Platform.

---

## 1. Frontend Architecture

- **Core Library**: React 18.2
- **Build System**: Vite 5.x (fast ES module bundling and hot module replacement)
- **Styling Framework**: Tailwind CSS 3.4 (utility-first styling without external bloat)
- **Icons**: Lucide React (clean, professional developer iconography)
- **HTTP Client**: Native Fetch API with structured request wrappers and JWT bearer interceptor
- **Routing**: Client-side stateful tab and route navigation with protected route guards

---

## 2. Backend Architecture

- **Runtime Environment**: Python 3.10+
- **Web Framework**: FastAPI 0.110+
  - High-performance asynchronous API endpoints
  - Interactive documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc)
- **Schema & Data Validation**: Pydantic v2
- **Server**: Uvicorn (ASGI server)
- **File Upload Parsing**: `python-multipart` for streaming multipart file processing

---

## 3. Storage & Persistence

- **Relational Database**: SQLite3 via SQLAlchemy 2.0 ORM
  - Zero-maintenance local ACID compliance
  - Tables: `users`, `bug_reports`, `agent_diagnoses`, `historical_defects`
- **Vector Database**: ChromaDB 0.4+
  - Local persistent vector storage (`chromadb.PersistentClient`)
  - Cosine distance similarity metric indexing
- **File Storage**: Local directory layout (`data/raw/`, `data/sample_data/`, `data/processed/`)

---

## 4. Artificial Intelligence & Vector Processing

- **Dense Embedding Model**: `sentence-transformers` (`all-MiniLM-L6-v2`)
  - Vector dimensionality: 384
  - Fully local, free, CPU-optimized embedding generation
- **LLM Reasoning & Orchestration**:
  - Direct REST API integration for Google Gemini (`gemini-1.5-flash` / `gemini-1.5-pro`) and OpenAI-compatible models
  - **Deterministic Local Heuristic Fallback Engine**: Built-in pattern-matching and expert rule engine allowing the complete 5-agent pipeline to run reliably without an external API key or internet connection.
- **Text Chunking**: Recursive character & code-block boundary splitter with metadata tagging

---

## 5. Security & Authentication

- **Password Hashing**: Passlib with `bcrypt` (salted, slow-hash resistant against rainbow tables)
- **Token Format**: JSON Web Tokens (JWT) via `python-jose`
- **Encryption Algorithm**: HMAC-SHA256 (`HS256`)
- **Transport Security**: Authorization Bearer header enforcement on all private endpoints

---

## 6. Testing & Tooling

- **Test Framework**: Pytest 8.x
- **HTTP Testing**: FastAPI `TestClient` (Starlette / HTTPX)
- **Environment Management**: `python-dotenv` for configuration injection
