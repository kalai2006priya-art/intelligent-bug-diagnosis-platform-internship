# System Architecture Specification

## 1. Overview
The **Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance** is engineered as a decoupled, multi-tier system uniting a modern Single Page Application (SPA), a high-performance RESTful API backend, an ACID relational database, a persistent local vector database, and a coordinated 5-agent AI orchestrator.

---

## 2. End-to-End System Pipeline

```
User (Developer)
      │
      ▼
Login / Signup (JWT Auth & Bcrypt)
      │
      ▼
Bug Submission / User Interface (Form + .txt/.log Upload)
      │
      ▼
Backend / API Layer (FastAPI Asynchronous Gateway)
      │
      ▼
Bug Report Upload & Storage (Validation & File Parsing)
      │
      ▼
Bug Report Processing Module
      │
      ▼
Bug Report / Submission Database (SQLite: Users, Bugs, Diagnoses)
      │
      ▼
Historical Defect Knowledge Base (Mozilla, Apache, Eclipse)
      │
      ▼
Data Cleaning & Chunking Pipeline (Normalization & Metadata Tagging)
      │
      ▼
Embedding Generation Module (all-MiniLM-L6-v2, 384 dimensions)
      │
      ▼
Vector Database / Semantic Search (ChromaDB Persistent Client)
      │
      ▼
RAG Retrieval Pipeline (Top-K Defect Retrieval + Similarity Scoring)
      │
      ▼
LLM / Reasoning Layer (Gemini / OpenAI API + Local Heuristic Fallback)
      │
      ▼
AI Agent Layer & Orchestrator
  ├── 1. Triage Agent (Severity, Priority, Component)
  ├── 2. Log Analysis Agent (Exception, Failure Point, Code Path)
  ├── 3. Root Cause Agent (RAG-grounded Hypothesis & Evidence Separation)
  ├── 4. Duplicate Detection Agent (Threshold Similarity Scoring)
  └── 5. Remediation Agent (Actionable Fixes & Validation Steps)
      │
      ▼
Structured Findings / Diagnosis Module (Consolidation & Validation)
      │
      ▼
Results & Recommendations Interface (6-Section Interactive Diagnostic Report)
      │
      ▼
Knowledge Base Update Module (Indexing New Verified Resolutions)
```

---

## 3. Core Architectural Subsystems

### Subsystem 1: User Interface Layer (Frontend)
- **Framework**: React 18, Vite build tool, Tailwind CSS.
- **Core Modules**:
  - **Auth Context**: JWT state retention in `localStorage` with automated authorization header attachment.
  - **Developer Dashboard**: High-level telemetry, bug count aggregates, recent status logs.
  - **Bug Submission Form**: Multipart form handler supporting structured input and file drag-and-drop (.txt, .log).
  - **Diagnostic Report Console**: Dedicated 6-section technical layout strictly distinguishing user inputs from retrieved evidence and model reasoning.
  - **Historical Defect Explorer**: Interactive knowledge base search and vector similarity tester.

### Subsystem 2: Application API Gateway (FastAPI Backend)
- **Framework**: FastAPI (Python 3.10+).
- **Sub-modules**:
  - **Security & Auth**: OAuth2 password bearer flow with bcrypt hashing and JWT token issuance.
  - **Bug Controller**: Request validation via Pydantic, file content inspection, and persistence invocation.
  - **Orchestration Dispatcher**: Coordinates the sequential and parallel execution of AI agents.
  - **Knowledge Base Controller**: Querying historical defect chunks and testing similarity metrics.

### Subsystem 3: Persistence & Storage Layer
- **Relational Store**: SQLite engine managed via SQLAlchemy ORM with schemas for `users`, `bug_reports`, `agent_diagnoses`, and `historical_defects`.
- **Vector Store**: ChromaDB running locally in persistent mode (`PersistentClient`) with cosine similarity indexing.
- **File System Storage**: Controlled directory tree (`data/raw/`, `data/sample_data/`, `data/processed/`).

### Subsystem 4: AI & Agent Orchestration Layer
- **Orchestrator**: Two-stage pipeline manager with explicit context-passing and failure tolerance:
  - **Stage 1**: Concurrent execution of `TriageAgent` and `LogAnalysisAgent`.
  - **Stage 2**: `RAGRetriever` queries ChromaDB using synthesized query context from Stage 1.
  - **Stage 3**: `RootCauseAgent` and `DuplicateDetectionAgent` consume Stage 1 findings + retrieved historical evidence.
  - **Stage 4**: `RemediationAgent` aggregates all hypotheses, duplicate match histories, and best practices to formulate structured remediation steps.
- **Resilience Strategy**: Every agent implements a dual-mode engine: external LLM integration when credentials are supplied, and deterministic, rule-based heuristic fallback if offline or unconfigured.
