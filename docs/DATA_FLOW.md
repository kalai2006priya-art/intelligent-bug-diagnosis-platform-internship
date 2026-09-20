# Data Flow Specification

## 1. High-Level Data Flow Summary

```
User
  │
  ▼
[Signup / Login] ──(Credentials)──> [FastAPI Backend] ──> [SQLite: Users]
                                            │
                                        (JWT Token)
                                            ▼
[Submit Bug] ─────(Bug Payload + File)───> [FastAPI Backend]
                                                │
                                    (Validation & File Parse)
                                                │
                                                ▼
                                    [SQLite: Bug Reports]
                                                │
                                                ▼
                                   [Agent Orchestrator]
                                     ├── [Triage Agent]
                                     └── [Log Analysis Agent]
                                                │
                                       (Parsed Symptoms)
                                                ▼
                                   [RAG Retrieval Engine]
                                                │
                                     (Query ChromaDB)
                                                ▼
                                [Top-K Historical Evidence]
                                                │
                                                ▼
                                     ├── [Root Cause Agent]
                                     └── [Duplicate Detection Agent]
                                                │
                                  (Hypothesis & Similarities)
                                                ▼
                                   [Remediation Agent]
                                                │
                                       (Fix & Verification)
                                                ▼
                                   [Structured Findings]
                                                │
                                                ▼
                                  [SQLite: Agent Diagnoses]
                                                │
                                                ▼
                                  [User Diagnostic Interface]
```

---

## 2. Step-by-Step Data Transformations

### Step 1: User Authentication Flow
1. Developer enters Full Name, Email, Password, and Confirmation on the Signup page.
2. Frontend sends `POST /api/auth/signup`.
3. Backend validates email uniqueness and password strength (min 6 chars). Password is salted and hashed using `bcrypt` and saved to `users` table.
4. Developer logs in with `POST /api/auth/login` (OAuth2 form-data or JSON).
5. Backend verifies hash, issues a signed JWT containing `sub=user_id`, with expiration.
6. Frontend stores token in `localStorage` and appends `Authorization: Bearer <token>` on all requests.

### Step 2: Bug Ingestion & File Parsing
1. User provides Title, Description, optional Component, Environment, Stack Trace, and Error Logs.
2. Optionally, user uploads a log or crash file (`.txt`, `.log`).
3. Endpoint `POST /bugs` or `POST /bugs/upload`:
   - Validates MIME type and extension (`.txt`, `.log`).
   - Checks file size limits (max 5 MB).
   - Reads text stream, detects character encoding (UTF-8/ASCII).
   - Automatically parses out stack trace blocks if detected in uploaded log content.
4. Record inserted into `bug_reports` table with status `"Submitted"`.

### Step 3: Stage 1 Agents (Triage & Log Analysis)
1. Orchestrator triggers:
   - `TriageAgent`: Reads title, description, component, environment. Outputs `severity`, `priority`, `affected_component`, `confidence`, and `reasoning`.
   - `LogAnalysisAgent`: Scans `stack_trace` and `error_logs`. Uses regex heuristics and LLM parser to extract `exception_type`, `error_message`, `failure_point`, and `affected_code_path`.
2. If no logs exist, `LogAnalysisAgent` yields `"Insufficient Evidence"`.

### Step 4: Semantic RAG Retrieval
1. Orchestrator constructs a composite search query: `"{title} | {exception_type} | {failure_point} | {description[:200]}"`.
2. `all-MiniLM-L6-v2` encodes query into 384-dimensional dense vector $\mathbf{q}$.
3. ChromaDB executes cosine similarity search against indexed chunks from Mozilla, Apache, and Eclipse.
4. Retrieves top 5 matching records including distance, project, chunk text, and resolution notes.

### Step 5: Stage 2 Agents (Root Cause & Duplicate Detection)
1. `RootCauseAgent` consumes:
   - User bug symptoms
   - Stage 1 parsed exception and failure point
   - Retrieved historical defect precedents
   - Generates grounded root cause hypothesis, separating facts from model deduction.
2. `DuplicateDetectionAgent`:
   - Evaluates cosine similarity of top matches.
   - If similarity $\ge 0.85 \implies$ `"Likely Duplicate"`.
   - If $0.65 \le \text{similarity} < 0.85 \implies$ `"Related Issue"`.
   - Otherwise $\implies$ `"New / Unmatched"`.

### Step 6: Stage 3 Agent (Remediation)
1. `RemediationAgent` consumes hypotheses, duplicate resolutions, and code path.
2. Formulates specific fixes:
   - Code changes / guards
   - Configuration tweaks
   - Step-by-step test validation procedures
   - Categorizes each recommendation as *Historical Evidence*, *General Best Practice*, or *Agent Recommendation*.

### Step 7: Persistence & Rendering
1. All agent outputs are packaged into a structured schema and persisted in `agent_diagnoses`.
2. Bug status transitions to `"Diagnosed"`.
3. Frontend renders the structured report in 6 clear, accessible sections.
