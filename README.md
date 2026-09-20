# Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance

An AI-assisted, multi-agent software defect diagnosis platform that combines runtime log parsing, semantic vector retrieval over historical defect repositories (**Mozilla**, **Apache**, and **Eclipse**), and coordinated reasoning to provide grounded root cause hypotheses, duplicate detection, and actionable code remediation.

---

## 1. Problem Statement & Objectives

Diagnosing software defects in production and development environments is time-consuming and prone to trial-and-error. Traditional defect workflows face recurring hurdles:
- **Superficial Log Analysis**: Developers often focus on the terminal crash frame (e.g. `NullPointerException`) rather than the underlying state corruption several frames earlier.
- **Ignored Historical Precedents**: Large open-source defect repositories (e.g. Mozilla Bugzilla, Apache Jira, Eclipse) contain millions of solved issues and verified patches, but developers rarely have fast semantic mechanisms to query them.
- **Duplicate Issue Overhead**: Triaging engineers spend excessive hours re-investigating defects that have already been documented and resolved.
- **Unverified AI Speculation**: Generic conversational LLMs frequently hallucinate plausible-sounding but ungrounded fixes without verifiable basis in project history.

### Objectives
1. **Automate Defect Triage**: Instantly classify defect severity, priority, and affected architectural component with confidence scoring.
2. **Deconstruct Runtime Traces**: Parse unstructured stack traces across Java, Python, C++, and JavaScript into standardized frames (failure point `file:line`, error message, and call hierarchy).
3. **Ground Reasoning with RAG**: Retrieve verified historical defect precedents from Mozilla, Apache, and Eclipse repositories to supply empirical context.
4. **Enforce Strict Evidence Separation**: Transparently isolate User Input, Retrieved Evidence, and Model Reasoning.
5. **Prescribe Actionable Remediation**: Generate specific code modifications, configuration adjustments, and step-by-step validation procedures.

---

## 2. System Architecture

```
User (Developer)
      │
      ▼
React Frontend (SPA) ──(JWT Bearer)──> FastAPI Backend
                                            │
                      ┌─────────────────────┼─────────────────────┐
                      ▼                     ▼                     ▼
               SQLite Database       ChromaDB Vector       Agent Orchestrator
             (Users, Bugs, Diags)  (384-d MiniLM Chunks)          │
                                                                  ▼
                                                       STAGE 1: Input Parsing
                                                       ├── 1. Triage Agent
                                                       └── 2. Log Analysis Agent
                                                                  │
                                                       STAGE 2: Semantic RAG
                                                       └── Query ChromaDB (Top-K)
                                                                  │
                                                       STAGE 3: Reasoning
                                                       ├── 3. Root Cause Agent
                                                       └── 4. Duplicate Detection Agent
                                                                  │
                                                       STAGE 4: Remediation
                                                       └── 5. Remediation Agent
                                                                  │
                                                       STAGE 5: Structured Report
                                                       └── Persisted to SQLite
```

---

## 3. The Five Specialized Diagnostic Agents

| Agent | Responsibility | Primary Outputs |
| :--- | :--- | :--- |
| **1. Triage Agent** | Rapid defect classification and subsystem mapping | `severity` (Critical/High/Medium/Low), `priority`, `affected_component`, `confidence`, `reasoning` |
| **2. Log Analysis Agent** | Deconstructs unstructured stack traces and error logs | `exception_type`, `error_message`, `failure_point` (`file:line`), `affected_code_path`, `confidence` |
| **3. Root Cause Agent** | Synthesizes symptoms with historical RAG evidence | `root_cause_hypothesis`, `supporting_evidence` list, `confidence`, `reasoning` |
| **4. Duplicate Detection Agent** | Quantifies semantic similarity against historical & submitted bugs | `status` (Likely Duplicate, Related Issue, New / Unmatched), `matches` with similarity scores |
| **5. Remediation Agent** | Formulates concrete code fixes and verification steps | `recommendations` categorized by basis (Historical Evidence vs General Best Practice vs Agent Recommendation), `suggested_code`, `validation_steps` |

---

## 4. Repository Directory Structure

```
bug-platform/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application, CORS, routers, lifespan
│   │   ├── config.py                  # Pydantic settings and env loader
│   │   ├── api/                       # REST API endpoints (auth, bugs, knowledge_base, health)
│   │   ├── agents/                    # 5 AI agents and AgentOrchestrator pipeline
│   │   ├── database/                  # SQLite session and table initializers
│   │   ├── models/                    # SQLAlchemy models (User, BugReport, AgentDiagnosis, HistoricalDefect)
│   │   ├── schemas/                   # Pydantic schemas for requests, responses, and agent outputs
│   │   ├── rag/                       # Chunker, embeddings (all-MiniLM-L6-v2), vector store (ChromaDB), retriever
│   │   ├── services/                  # Business logic (AuthService, BugService, LLMService)
│   │   └── utils/                     # Password hashing, JWT tokens, regex stack trace parsers
│   └── requirements.txt               # Backend Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── api/                       # Fetch API client and service endpoints
│   │   ├── components/                # Navbar, Sidebar, ProtectedRoute, StatusBadge, ProgressTracker
│   │   ├── context/                   # AuthContext with persistent JWT session
│   │   ├── pages/                     # Landing, Login, Signup, Dashboard, SubmitBug, History, Diagnosis, KnowledgeBase, Profile
│   │   ├── App.jsx                    # Root view and navigation dispatcher
│   │   └── main.jsx                   # React 18 DOM mount
│   ├── package.json                   # React, Vite, Tailwind CSS, Lucide icons
│   └── vite.config.js                 # Dev server configuration with backend proxy
│
├── data/
│   ├── raw/
│   │   ├── mozilla/                   # Place downloaded Mozilla Kaggle dataset files here
│   │   ├── apache/                    # Place downloaded Apache Kaggle dataset files here
│   │   └── eclipse/                   # Place downloaded Eclipse Kaggle dataset files here
│   ├── sample_data/                   # Curated defect samples for immediate offline execution
│   │   ├── mozilla_sample.json
│   │   ├── apache_sample.json
│   │   └── eclipse_sample.json
│   ├── processed/                     # Standardized chunk storage
│   └── README.md                      # Comprehensive dataset instructions
│
├── docs/
│   ├── RESEARCH.md                    # Defect workflows, RAG, similarity mathematics
│   ├── SYSTEM_ARCHITECTURE.md         # Full architectural breakdown
│   ├── ARCHITECTURE_DIAGRAM.drawio    # Draw.io compatible XML system diagram
│   ├── AGENT_RESPONSIBILITIES.md      # Detailed 5-agent specifications
│   ├── AGENT_ORCHESTRATION.md         # Stage-by-stage pipeline flow
│   ├── BUG_REPORT_SCHEMA.md           # Bug report schema and DB mapping
│   ├── KNOWLEDGE_BASE_SCHEMA.md       # Knowledge base schema and Kaggle column mapping
│   ├── DATA_FLOW.md                   # Step-by-step data flow guide
│   ├── TECH_STACK.md                  # Exact verified technologies
│   └── MILESTONE_MAPPING.md           # Complete line-by-line requirement mapping
│
├── scripts/
│   ├── process_datasets.py            # Universal dataset loader, cleaner, chunker & indexer
│   └── test_semantic_retrieval.py     # CLI tool to test vector similarity against knowledge base
│
├── tests/
│   ├── conftest.py                    # Pytest test fixtures and DB setup
│   ├── test_auth.py                   # Signup, login, duplicate check, JWT security
│   ├── test_bugs.py                   # Bug creation, file upload (.txt/.log), validation
│   ├── test_triage_agent.py           # Severity, priority, component, insufficient evidence
│   ├── test_log_analysis_agent.py     # Java NPE, Python traceback, missing logs
│   ├── test_rag_and_vector_store.py   # Embeddings, chunking, ChromaDB queries
│   ├── test_root_cause_agent.py       # Grounded hypothesis and evidence citations
│   ├── test_duplicate_agent.py        # Similarity thresholds (Likely Duplicate, Related, New)
│   ├── test_remediation_agent.py      # Actionable code fixes and validation steps
│   └── test_orchestration.py          # Full 5-agent end-to-end integration test
│
├── .env.example                       # Configuration template
├── .gitignore                         # Excludes large Kaggle files, node_modules, .env
└── README.md                          # This documentation file
```

---

## 5. Technology Stack

- **Frontend**: React 18, Vite 5, Tailwind CSS 3.4, Lucide React icons.
- **Backend API**: FastAPI, Uvicorn, Pydantic v2.
- **Database**: SQLite3 via SQLAlchemy 2.0 ORM.
- **Vector Database**: ChromaDB (PersistentClient with cosine similarity metric).
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) with deterministic fallback.
- **Authentication**: JWT tokens (HMAC-SHA256) and Passlib (Bcrypt password hashing).
- **Testing**: Pytest 8.x with FastAPI `TestClient`.

---

## 6. Installation & Setup (Windows PowerShell)

### Prerequisites
- Python 3.10+
- Node.js v18+ and npm

### Step 1: Clone or Navigate to Project
```powershell
cd C:\Users\HP\.gemini\antigravity\scratch\bug-platform
```

### Step 2: Configure Environment
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```

### Step 3: Install Backend Dependencies
```powershell
python -m pip install -r backend/requirements.txt
```

### Step 4: Ingest Historical Datasets
To load and index the bundled sample datasets (Mozilla, Apache, Eclipse) immediately:
```powershell
python scripts/process_datasets.py --sample
```

*(Optional)* If you have downloaded Kaggle datasets:
1. Place Mozilla CSV/JSON files in `data/raw/mozilla/`
2. Place Apache CSV/JSON files in `data/raw/apache/`
3. Place Eclipse CSV/JSON files in `data/raw/eclipse/`
4. Run:
```powershell
python scripts/process_datasets.py
```

### Step 5: Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

## 7. How to Run the Application

### 1. Start the FastAPI Backend
In your first PowerShell terminal:
```powershell
cd C:\Users\HP\.gemini\antigravity\scratch\bug-platform\backend
python -m uvicorn app.main:app --reload --port 8000
```
- API Root: `http://localhost:8000/`
- Interactive OpenAPI / Swagger Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Start the React Frontend
In a second PowerShell terminal:
```powershell
cd C:\Users\HP\.gemini\antigravity\scratch\bug-platform\frontend
npm run dev
```
- Application UI: `http://localhost:5173/`

---

## 8. User Workflow Guide

1. **Sign Up**: Open `http://localhost:5173/`, click **Get Started** or **Sign Up**, and create an account (Full Name, Email, Password min 6 chars).
2. **Sign In**: Log in with your registered email and password. Your JWT token will be stored securely in `localStorage`.
3. **Submit Bug**:
   - Navigate to **Submit Bug** from the sidebar.
   - Enter Title (e.g. `Login fails with NullPointerException`) and Description.
   - Optionally upload a `.txt` or `.log` crash file using the **Upload** button to automatically populate stack traces and operational logs.
   - Click **Submit & Analyze Bug**.
4. **Observe Real-Time Progress**: Watch the 7-stage multi-agent orchestration progress tracker execute in real time.
5. **Review Diagnosis Report**:
   - Inspect the 6 distinct report sections.
   - Verify that **User Input**, **Retrieved Historical Evidence**, and **Agent Reasoning** are strictly separated.
   - Copy suggested remediation code snippets and review step-by-step verification procedures.
6. **Explore Knowledge Base**:
   - Navigate to **Knowledge Base** from the sidebar.
   - Filter records by Mozilla, Apache, or Eclipse.
   - Test vector queries using the interactive semantic similarity search bar.

---

## 9. Running Automated Tests

Run the complete test suite covering authentication, bug submission, file upload, individual agents, vector retrieval, and end-to-end orchestration:
```powershell
cd C:\Users\HP\.gemini\antigravity\scratch\bug-platform
python -m pytest tests/ -v
```

To test vector retrieval via CLI:
```powershell
python scripts/test_semantic_retrieval.py --query "Null pointer crash in HTTP response listener"
```

---

## 10. API Specification Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health check and ChromaDB chunk count |
| `GET` | `/` | Root platform overview |
| `POST` | `/api/auth/signup` | Register developer account |
| `POST` | `/api/auth/login` | Authenticate user and issue JWT token |
| `GET` | `/api/auth/me` | Fetch authenticated developer profile |
| `POST` | `/bugs` | Submit a defect report |
| `POST` | `/bugs/upload` | Upload and parse `.txt` or `.log` file |
| `GET` | `/bugs` | List submitted bug reports |
| `GET` | `/bugs/{bug_id}` | Retrieve specific bug details |
| `POST` | `/bugs/{bug_id}/analyze` | Execute 5-agent diagnosis orchestration |
| `GET` | `/bugs/{bug_id}/diagnosis` | Fetch structured 6-section diagnostic report |
| `GET` | `/api/knowledge-base/defects` | Filter and browse historical defect records |
| `POST` | `/api/knowledge-base/search` | Execute semantic vector search |
| `GET` | `/api/knowledge-base/stats` | Defect counts per dataset repository |

---

## 11. Honest Limitations & Ethical AI Disclosures

- **Probabilistic Hypotheses**: Root-cause conclusions and fix recommendations represent algorithmic inferences based on available context and historical precedent. They do not constitute a 100% guarantee of resolution without human verification.
- **Data Quality Sensitivity**: If a submitted defect report lacks descriptive details or stack traces, the system will explicitly report **Insufficient Evidence** rather than manufacturing synthetic facts.
- **Defect Dataset Scope**: Historical evidence is bounded by the public defect knowledge base (Mozilla, Apache, Eclipse) indexed in the local vector store.
