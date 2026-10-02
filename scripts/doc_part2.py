"""
Part 2 of M4.4 Technical Documentation:
Section 4, Section 5, Section 6, Section 7
"""

SECTION_4 = """# Section 4 — Bug Submission Module

### 4.1 Form Fields & Input Modalities
The Bug Submission Module ([`frontend/src/pages/SubmitBugPage.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/pages/SubmitBugPage.jsx)) provides an intuitive interface for developers, testers, and automated monitoring systems to report software defects. 

The module captures both high-level symptom descriptions and technical low-level execution context:

| Form Field | Data Type | Required? | Description & Purpose |
| :--- | :--- | :---: | :--- |
| **Bug Title** | String (5–250 chars) | **Yes** | Concise summary of the observed defect or error |
| **Description** | Text (min 15 chars) | **Yes** | Detailed explanation of steps to reproduce, user expectations, and failure behavior |
| **Component** | String (optional) | No | Target architectural module (e.g., `Authentication`, `Database`, `UI`, `Networking`) |
| **Environment** | String (optional) | No | Host operating system, browser version, runtime JVM/Python version, or container platform |
| **Stack Trace** | Text (optional) | No | Raw execution stack frame text copied from console or debugger |
| **Error Logs** | Text (optional) | No | Log entries, timestamped warnings, or runtime application error outputs |

```
+-------------------------------------------------------------------------------+
|                                                                               |
|            [Screenshot: Bug Submission Interface — to be captured             |
|                        from running application]                              |
|                                                                               |
+-------------------------------------------------------------------------------+
Figure 4.1: Bug Submission Form with Direct Text and File Upload Modalities.
```

### 4.2 Log File & Stack Trace Ingestion
In addition to direct manual text entry, the platform features a file upload ingestion system. Users can upload crash dumps or raw operational log files directly:
- **Supported File Extensions**: `.log`, `.txt`.
- **Upload File Size Limit**: Configured up to **10 Megabytes**.
- **MIME Validation**: Validates text file encodings (UTF-8, ASCII) and blocks executable formats (`.exe`, `.bin`, `.sh`) via HTTP 400 Bad Request error handling.

### 4.3 Ingestion Parsing Heuristics
When a log file is uploaded via `POST /bugs/upload`, the backend invokes `parse_uploaded_log_file()` in [`backend/app/utils/parsers.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/utils/parsers.py). This function automatically splits unstructured log dumps into clean database fields:
1. **Title Extraction**: Automatically inspects the first non-comment line of the uploaded file and assigns it as the tentative title.
2. **Stack Trace Detection**: Identifies lines starting with standard stack frame indicators (`"at "`, `"Traceback"`, `"File \""`, `"Exception in"`, `"Crash [@"`) and aggregates them into the `stack_trace` field.
3. **Error Log Extraction**: Isolates timestamped warning/error statements (`[ERROR]`, `[WARN]`, `FATAL`) and populates the `error_logs` field.
4. **Description Generation**: Generates an informative summary stating the original filename, total line count, and a preview of the initial log headers.

### 4.4 Source Files & UI Artifacts
- **Frontend Form**: [`frontend/src/pages/SubmitBugPage.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/pages/SubmitBugPage.jsx)
- **Frontend API Client**: [`frontend/src/api/bugs.js`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/api/bugs.js)
- **Backend API Endpoints**: [`backend/app/api/bugs.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/api/bugs.py) (`POST /bugs`, `POST /bugs/upload`)
- **Parsing Utilities**: [`backend/app/utils/parsers.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/utils/parsers.py)

---
"""

SECTION_5 = """# Section 5 — Historical Defect Knowledge Base

### 5.1 Purpose & Role in Diagnostics
A central limitation of conventional bug trackers is that they treat each newly reported defect as an isolated incident. In reality, modern software defects frequently exhibit strong recurrence patterns: similar memory leaks, concurrency race conditions, null pointer dereferences, and socket timeout patterns have typically been encountered and solved before.

The **Historical Defect Knowledge Base** serves as the empirical ground-truth repository of the platform. It provides high-quality software engineering precedents that ground the **Root Cause Agent**, inform the **Duplicate Detection Agent**, and furnish verified code patches for the **Remediation Agent**.

### 5.2 Open-Source Historical Repositories (Mozilla, Apache, Eclipse)
The platform is seeded with curated defect repositories extracted from major open-source ecosystems:
- **Mozilla Bugzilla**: Desktop and browser runtime defects from Firefox and Gecko, characterized by C++ access violations, native thread assertions, and stream cancellation crashes.
- **Apache Jira**: High-throughput distributed systems defects from Hadoop, Lucene, and Commons, featuring Java concurrency deadlocks, I/O connection starvation, and configuration timeouts.
- **Eclipse Bugzilla**: Rich client and IDE runtime defects, characterized by SWT thread access violations, class loader exceptions, and UI event loop locks.

```
+-------------------------------------------------------------------------------+
|                                                                               |
|            [Screenshot: Historical Defect Knowledge Base Explorer —           |
|                     to be captured from running application]                  |
|                                                                               |
+-------------------------------------------------------------------------------+
Figure 5.1: Knowledge Base Explorer Interface with Source Filtering and Live Search.
```

### 5.3 Platform-Contributed Defect Records
Through the **Knowledge Base Growth Mechanism** (M4.2), the knowledge base is not static. When a platform defect is successfully resolved by an engineer and its fix is verified through the Quality Gate, it is assigned a permanent identifier (`PLATFORM-<HEX>`) and indexed with `dataset_source="Platform"`. These platform-contributed records immediately participate in all future RAG retrieval queries.

### 5.4 Database Storage & Index Statistics
The audited state of the knowledge base demonstrates clean dual-store synchronization:
- **Relational Defect Records (`historical_defects` table)**: **14 baseline historical records** seeded in SQLite across Mozilla (5), Apache (5), and Eclipse (4).
- **ChromaDB Vector Chunks (`historical_defects` collection)**: **51 active dense vector chunks** (dimension: 384) indexed via HNSW.
- **Query Interfaces**:
  - Relational filtering by source, project, or component via `GET /api/knowledge-base/defects`.
  - Semantic vector similarity retrieval via `POST /api/knowledge-base/search`.
  - Aggregated source counts via `GET /api/knowledge-base/stats`.

---
"""

SECTION_6 = """# Section 6 — Data Model & Schema Specifications

### 6.1 Relational Database Schema (SQLAlchemy)
The relational persistence layer is managed via SQLAlchemy ORM models mapped to SQLite tables in [`backend/app/models/`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/models/):

#### 1. `users` Table ([`backend/app/models/user.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/models/user.py))
Stores platform user credentials and administrative access roles.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | Primary Key, UUID | Unique user identifier |
| `email` | VARCHAR(255) | Unique, Not Null, Index | User login email address |
| `name` | VARCHAR(255) | Not Null | User full name |
| `password_hash` | VARCHAR(255) | Not Null | Cryptographic bcrypt hashed password |
| `role` | VARCHAR(50) | Default: `'developer'` | Role: developer, tester, admin |
| `created_at` | DATETIME | Default: `utcnow` | User account creation timestamp |

#### 2. `bug_reports` Table ([`backend/app/models/bug_report.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/models/bug_report.py))
Stores user-submitted defect records and lifecycle resolution states.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | Primary Key, UUID | Unique bug report identifier |
| `user_id` | VARCHAR(36) | Foreign Key (`users.id`), Nullable | Submitting user ID |
| `title` | VARCHAR(255) | Not Null, Index | Concise defect title |
| `description` | TEXT | Not Null | Detailed defect description |
| `stack_trace` | TEXT | Nullable | Raw stack trace or traceback text |
| `error_logs` | TEXT | Nullable | Application execution log dump |
| `component` | VARCHAR(100) | Nullable | Architectural component |
| `environment` | VARCHAR(255) | Nullable | Host OS, browser, runtime version |
| `status` | VARCHAR(50) | Default: `'Submitted'` | Status: Submitted, Diagnosed, Resolved, Closed |
| `resolution_notes` | TEXT | Nullable | Developer explanation of confirmed fix (M4.2) |
| `confirmed_fix_code`| TEXT | Nullable | Actionable code patch applied (M4.2) |
| `resolved_at` | DATETIME | Nullable | Timestamp of verified resolution |
| `indexed_in_kb` | BOOLEAN | Default: `False` | True if defect has been promoted to ChromaDB |
| `created_at` | DATETIME | Default: `utcnow` | Submission timestamp |
| `updated_at` | DATETIME | Default: `utcnow` | Last update timestamp |

#### 3. `agent_diagnoses` Table ([`backend/app/models/diagnosis.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/models/diagnosis.py))
Stores the structured diagnostic findings generated by the 5-agent pipeline.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | Primary Key, UUID | Unique diagnosis report identifier |
| `bug_id` | VARCHAR(36) | Foreign Key (`bug_reports.id`), Not Null | Associated defect report ID |
| `status` | VARCHAR(50) | Default: `'Completed'` | Diagnosis state: Completed, Failed |
| `overall_confidence`| FLOAT | Not Null | Average confidence score across agents $[0.0, 1.0]$ |
| `triage_json` | TEXT | Not Null | Serialized JSON from Triage Agent |
| `log_analysis_json` | TEXT | Not Null | Serialized JSON from Log Analysis Agent |
| `root_cause_json` | TEXT | Not Null | Serialized JSON from Root Cause Agent |
| `duplicate_detection_json` | TEXT | Not Null | Serialized JSON from Duplicate Detection Agent |
| `remediation_json` | TEXT | Not Null | Serialized JSON from Remediation Agent |
| `created_at` | DATETIME | Default: `utcnow` | Timestamp of diagnosis completion |
| `updated_at` | DATETIME | Default: `utcnow` | Last update timestamp |

#### 4. `historical_defects` Table ([`backend/app/models/historical_defect.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/models/historical_defect.py))
Stores historical ground-truth defects used for RAG retrieval and knowledge base queries.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | VARCHAR(36) | Primary Key, UUID | Unique internal record ID |
| `dataset_source` | VARCHAR(50) | Not Null, Index | Mozilla, Apache, Eclipse, or Platform |
| `project` | VARCHAR(100) | Not Null | Project name (e.g., Firefox, Hadoop, Platform) |
| `bug_id` | VARCHAR(50) | Not Null, Index | Upstream defect ID (e.g., `MOZ-459102`, `PLATFORM-01`) |
| `title` | VARCHAR(255) | Not Null | Historical defect title |
| `description` | TEXT | Not Null | Historical defect description |
| `stack_trace` | TEXT | Nullable | Associated stack frame dump |
| `error_message` | TEXT | Nullable | Primary exception or error message |
| `component` | VARCHAR(100) | Nullable | Subsystem or component |
| `severity` | VARCHAR(50) | Nullable | Historical severity rating |
| `priority` | VARCHAR(50) | Nullable | Historical priority rating |
| `resolution` | TEXT | Nullable | Documented resolution and fix description |
| `status` | VARCHAR(50) | Default: `'CLOSED'` | Upstream resolution status |
| `comments` | TEXT | Nullable | Developer comments or patch notes |
| `source_reference` | VARCHAR(255) | Nullable | URL or citation to original defect report |
| `created_at` | DATETIME | Default: `utcnow` | Record ingestion timestamp |

### 6.2 Entity Relationship Analysis
```
┌──────────────┐         1:N          ┌─────────────────┐         1:1          ┌──────────────────┐
│    users     │ ──────────────────── │   bug_reports   │ ──────────────────── │ agent_diagnoses  │
│--------------│                      │-----------------│                      │------------------│
│ id (PK)      │                      │ id (PK)         │                      │ id (PK)          │
│ email        │                      │ user_id (FK)    │                      │ bug_id (FK)      │
│ name         │                      │ title           │                      │ overall_conf     │
│ password_hash│                      │ description     │                      │ triage_json      │
│ role         │                      │ status          │                      │ log_analysis_json│
└──────────────┘                      │ indexed_in_kb   │                      │ root_cause_json  │
                                      └─────────────────┘                      │ duplicate_json   │
                                                                               │ remediation_json │
                                                                               └──────────────────┘
                                      ┌─────────────────────┐
                                      │ historical_defects  │
                                      │---------------------│
                                      │ id (PK)             │
                                      │ dataset_source      │
                                      │ bug_id (Indexed)    │
                                      │ title, description  │
                                      │ resolution, comments│
                                      └─────────────────────┘
```

### 6.3 Pydantic Data Transfer Objects & Validation Schemas
The application defines strict request and response schemas in [`backend/app/schemas/`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/schemas/):
- **`BugCreate` / `BugResponse`**: Enforces title length $\ge 5$, description $\ge 15$, and handles optional stack traces.
- **`TriageResult`**: Validates severity in `['Critical', 'High', 'Medium', 'Low']`, priority in `['Critical', 'High', 'Medium', 'Low']`, affected component, confidence $[0.0, 1.0]$, and reasoning string.
- **`LogAnalysisResult`**: Validates status in `['Success', 'Insufficient Evidence']`, exception type, failure point (`file:line`), and call path.
- **`RootCauseResult`**: Validates status in `['Supported', 'Insufficient Evidence']`, hypothesis, supporting evidence array, and reasoning.
- **`DuplicateDetectionResult`**: Validates status in `['Likely Duplicate', 'Related Issue', 'New / Unmatched', 'Insufficient Evidence']`, and ranked matches list.
- **`RemediationResult`**: Validates status, recommendation items with basis in `['Historical Evidence', 'General Best Practice', 'Agent Recommendation']`, suggested code snippets, and validation steps.
- **`ResolutionSubmission` / `PromotionResponse`**: Validates verified resolution notes ($\ge 10$ chars), confirmed fix code patch, and returned vector promotion confirmation.

---
"""

SECTION_7 = """# Section 7 — RAG Pipeline

### 7.1 End-to-End RAG Architecture
The **Retrieval-Augmented Generation (RAG)** pipeline grounds the diagnosis agents by surfacing relevant historical defect precedents from ChromaDB.

```mermaid
graph LR
    subgraph Offline_Ingestion ["1. Ingestion & Indexing Pipeline"]
        Raw_Data["Raw Historical JSON\n(Mozilla, Apache, Eclipse)"]
        Clean["Data Standardization\n(clean_datasets.py)"]
        Chunk["Multi-Section Chunker\n(chunker.py)"]
        Embed["Embedding Service\n(all-MiniLM-L6-v2)"]
        Chroma[("ChromaDB Vector Store\n(chroma_db/)")]

        Raw_Data --> Clean --> Chunk --> Embed --> Chroma
    end

    subgraph Online_Retrieval ["2. Online Diagnostic Querying"]
        Bug_Input["New Bug Submission\n(Title, Logs, Exception)"]
        Query_Gen["Contextual Query Construction\n(retriever.py)"]
        Query_Vec["Dense Query Vectorization\n(384 dimensions)"]
        KNN_Search["HNSW Cosine Vector Search\n(top_k=5)"]
        Context["Retrieved Historical Precedents\n(Similarity, Resolution, Fix)"]

        Bug_Input --> Query_Gen --> Query_Vec --> KNN_Search
        Chroma -.-> KNN_Search
        KNN_Search --> Context
    end

    subgraph Agent_Injection ["3. Agent Grounding"]
        RC_Agent["Root Cause Agent\n(Grounds Hypothesis)"]
        Dup_Agent["Duplicate Detection Agent\n(Evaluates Thresholds)"]
        Rem_Agent["Remediation Agent\n(Adapts Fix Code)"]

        Context --> RC_Agent
        Context --> Dup_Agent
        Context --> Rem_Agent
    end
```

### 7.2 Document Chunking Strategy
Historical defects often exceed optimal embedding window lengths due to lengthy stack traces and log dumps. The platform uses a structured semantic chunking algorithm implemented in `chunk_historical_bug()` ([`backend/app/rag/chunker.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/rag/chunker.py)):
1. **Header & Description Chunk**: Combines defect title, component, and user symptom description. This chunk captures high-level behavioral symptoms.
2. **Error & Stack Frame Chunk**: Isolates raw stack trace frames and exception messages. This chunk is optimized for technical failure signature matching.
3. **Resolution & Patch Chunk**: Isolates developer comments, root cause discussions, and confirmed code fixes.
4. **Metadata Preservation**: Every chunk retains strict metadata attributes: `bug_id`, `source`, `project`, `component`, `title`, `resolution`, and `chunk_id`.

### 7.3 Dense Vector Embeddings (384-d all-MiniLM-L6-v2)
Text chunks are vectorized via `EmbeddingService` in [`backend/app/rag/embeddings.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/rag/embeddings.py):
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Dimension**: **384 dense floating-point values**
- **Normalization**: Embeddings are unit-normalized ($L_2$ norm $= 1.0$), ensuring that the inner product directly corresponds to cosine similarity.
- **Deterministic Offline Fallback**: If the `sentence-transformers` library or model weights are unavailable, the service activates an internal deterministic term-frequency cosine engine, ensuring the platform remains fully testable without external downloads.

### 7.4 Vector Store Indexing & ChromaDB Engine
Persistent vector storage is handled via `VectorStore` in [`backend/app/rag/vector_store.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/rag/vector_store.py):
- **Client**: `chromadb.PersistentClient(path="chroma_db")`
- **Collection Name**: `historical_defects`
- **Distance Metric**: Configured with cosine distance space (`metadata={"hnsw:space": "cosine"}`).
- **Upsert Semantics**: Supports atomic `add_chunks()` using `collection.upsert()`, allowing non-disruptive insertions for both baseline historical defects and platform-promoted defects (M4.2).

### 7.5 Retrieval Query Construction & Similarity Scoring
When a bug enters Stage 2 of diagnosis, `RAGRetriever` in [`backend/app/rag/retriever.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/rag/retriever.py) constructs an enriched retrieval query:
$$\text{Query} = \text{Title} + \text{" "} + \text{ExceptionType} + \text{" "} + \text{FailurePoint} + \text{" "} + \text{Description}_{[:200]}$$

ChromaDB returns nearest neighbors along with their cosine distance $D_{\text{cos}} \in [0, 2]$. The retriever maps distance to a normalized similarity score $S \in [0.0, 1.0]$:
$$S = 1.0 - \frac{D_{\text{cos}}}{2.0}$$

Top-$k$ results ($k=5$ by default) are filtered and passed to the downstream agents as structured dictionaries containing metadata, title, resolution summary, and similarity metrics.

---
"""

print("Part 2 defined successfully.")
