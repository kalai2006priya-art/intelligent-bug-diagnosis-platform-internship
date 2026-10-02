"""
Part 4 of M4.4 Technical Documentation:
Section 11, Section 12, Section 13, Section 14
"""

SECTION_11 = """# Section 11 — Structured Findings Display (UI / Frontend)

### 11.1 Report Page Architecture
The **Structured Findings Display** is implemented in [`frontend/src/pages/DiagnosisReportPage.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/pages/DiagnosisReportPage.jsx). It serves as the primary developer cockpit, transforming raw diagnostic telemetry and multi-agent outputs into an organized, readable, and actionable 7-section report.

The interface adheres to modern developer-tool UX design principles:
- **Visual Hierarchy**: High-level severity, priority, and confidence metrics are highlighted in prominent top-level banner cards, followed by deep technical details (stack frames, root cause evidence, deduplication matches, code fixes).
- **Collapsible / Modular Cards**: Each diagnostic section is encapsulated in a dedicated card with clear iconography (Lucide icons), distinct border styling, and contextual color palettes.
- **Copy-Paste Convenience**: All generated code recommendations include syntax-highlighted code blocks with one-click clipboard copy buttons.
- **Auditable Provenance**: Diagnostic claims link directly to underlying historical defect IDs or general best-practice classifications.

```
+-------------------------------------------------------------------------------+
|                                                                               |
|            [Screenshot: Structured Findings Dashboard (Overview,              |
|                 Triage, Log Analysis) — to be captured from                   |
|                            running application]                               |
|                                                                               |
+-------------------------------------------------------------------------------+
Figure 11.1: Structured Findings Dashboard — Header, Triage, and Log Analysis Cards.
```

### 11.2 Anatomy of the 7 Diagnostic Report Sections

The report page is divided into seven dedicated diagnostic panels:

#### Section 1: Overall Diagnosis Header & Status
- **Bug Title & Tracking ID**: Displays the bug ID (UUID) and user-provided defect summary.
- **Workflow State Badge**: Displays current defect lifecycle state (`"Submitted"`, `"Analyzing"`, `"Diagnosed"`, `"Resolved"`).
- **Overall Confidence Meter**: Displays the combined multi-agent confidence score ($0.00$ to $1.00$) with color-coded gauge styling:
  - Green ($\ge 0.85$): High diagnostic confidence.
  - Yellow ($0.60$ to $0.84$): Moderate diagnostic confidence.
  - Orange / Red ($< 0.60$): Low confidence due to partial or sparse logs.
- **Action Triggers**: Quick-action buttons to re-run analysis or mark the bug as resolved.

#### Section 2: Defect Triage & Severity
- **Severity Badge**: Color-coded indicator (`Critical` - Red, `High` - Orange, `Medium` - Yellow, `Low` - Blue).
- **Priority Badge**: Recommended SLA operational urgency.
- **Affected Subsystem**: Target architectural component classified by the Triage Agent (e.g., `Authentication & Authorization`, `Database / Persistence`, `UI & Frontend Rendering`).
- **Triage Reasoning**: Natural language explanation detailing the keyword matches and failure cues that determined the classification.

#### Section 3: Log & Stack Trace Analysis
- **Execution Status**: Indicates whether stack traces were successfully parsed (`"Success"`) or flagged (`"Insufficient Evidence"`).
- **Exception Class**: The extracted runtime exception or error name (e.g., `NullPointerException`, `ZeroDivisionError`, `TypeError`, `NativeCrashException`).
- **Failure Point**: The exact source file and line number where the fault was triggered (e.g., `AuthService.java:55`, `analytics_worker.py:108`).
- **Affected Code Path**: The execution call stack hierarchy showing the sequence of caller methods leading to the exception.

```
+-------------------------------------------------------------------------------+
|                                                                               |
|              [Screenshot: Root Cause & Duplicate Detection                    |
|             Finding Cards — to be captured from running application]          |
|                                                                               |
+-------------------------------------------------------------------------------+
Figure 11.2: Root Cause Hypothesis & Semantic Duplicate Match Finding Cards.
```

#### Section 4: Root Cause Analysis
- **Root Cause Hypothesis**: The probable underlying technical flaw causing the defect.
- **Causal Reasoning**: Deductive explanation linking the observed failure point with historical precedents.
- **Supporting Historical Evidence Cards**: Visual cards displaying top retrieved precedents ($S > 0.40$), including historical Bug ID, source repository badge (Mozilla, Apache, Eclipse), similarity score, and excerpt of the historical resolution.

#### Section 5: Duplicate & Related Issues
- **Deduplication Status Badge**:
  - `Likely Duplicate` (?? Red, $S \ge 0.85$): Matches an existing defect.
  - `Related Issue` (?? Yellow, $0.65 \le S < 0.85$): Shares component or symptom patterns.
  - `New / Unmatched` (?? Green, $S < 0.65$): Unique defect.
- **Ranked Match Cards**: List of top-5 matching candidates showing similarity percentage progress bar, bug title, component, and resolution summary.

```
+-------------------------------------------------------------------------------+
|                                                                               |
|           [Screenshot: Remediation Action Plan & Code Fix Viewer              |
|                   — to be captured from running application]                  |
|                                                                               |
+-------------------------------------------------------------------------------+
Figure 11.3: Actionable Code Fix Viewer with Provenance Badges and Validation Steps.
```

#### Section 6: Actionable Fix Recommendations
- **Recommendation Summary**: Concise statement of the required code or architectural fix.
- **Provenance Basis Badge**: Explicitly identifies whether the recommendation is based on:
  - ??? `Historical Evidence` (grounded in an accepted historical patch).
  - ??? `General Best Practice` (established industry coding standard).
  - ??? `Agent Recommendation` (heuristic synthesis).
- **Suggested Code Snippet**: Pre-formatted syntax-highlighted code block demonstrating defensive validation, null checks, or configuration adjustments. Includes an active one-click copy button.
- **Verification & Validation Checklist**: Step-by-step testing instructions for QA engineers and developers to verify the fix.

#### Section 7: Knowledge Base Growth Promotion Card
- Implemented via [`frontend/src/components/growth/ResolutionPromotionCard.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/components/growth/ResolutionPromotionCard.jsx).
- Displays the current resolution status and allows developers to enter verified fix notes.
- Performs real-time **Quality Gate Validation** and enables one-click promotion into the ChromaDB vector knowledge base.

### 11.3 UI State Management & Polling
The frontend utilizes React 18 local state and asynchronous lifecycle hooks (`useEffect`):
- **Staged Progress Animation**: When `/analyze` is triggered, the UI renders an animated multi-step progress bar cycling through:
  `Triage -> Log Parsing -> Semantic RAG -> Root Cause -> Deduplication -> Remediation -> Findings Ready`.
- **Optimistic UI Updates**: Status changes (e.g., submitting a resolution) update the local component state immediately before re-fetching from the server.
- **Defensive Rendering**: If optional diagnostic sections are empty or flagged as `"Insufficient Evidence"`, the UI displays informative alert notices rather than blank white screens.

### 11.4 Source Files & Component Structure
- **Report Page**: [`frontend/src/pages/DiagnosisReportPage.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/pages/DiagnosisReportPage.jsx)
- **Status Badge**: [`frontend/src/components/StatusBadge.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/components/StatusBadge.jsx)
- **Progress Tracker**: [`frontend/src/components/ProgressTracker.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/components/ProgressTracker.jsx)
- **Promotion Card**: [`frontend/src/components/growth/ResolutionPromotionCard.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/components/growth/ResolutionPromotionCard.jsx)
- **API Client**: [`frontend/src/api/bugs.js`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/api/bugs.js) and [`frontend/src/api/growth.js`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/api/growth.js)

---
"""

SECTION_12 = """# Section 12 — Knowledge Base Growth Mechanism (M4.2)

### 12.1 Purpose & Role in Platform Self-Improvement
In conventional bug tracking systems, once a defect is resolved, the developer notes and code patches are archived in relational database tables where they rarely inform future investigations. 

The **Knowledge Base Growth Mechanism** (developed in Milestone 4.2) creates an active, continuous learning loop. It transforms newly resolved software defects into permanent institutional intelligence by indexing approved defect records into the **ChromaDB** vector store as 384-dimensional dense vectors. 

As developers resolve bugs on the platform, subsequent defect diagnoses benefit from richer historical precedent data, higher semantic retrieval similarity, and better fix recommendations.

### 12.2 Lifecycle of a Resolved Bug Promotion

The promotion of a defect follows a strict four-stage operational lifecycle:

```
[Defect Diagnosed] 
        ?
        ?
[Stage 1: Developer Resolution]
Developer enters confirmed root cause, verified code patch, and marks bug "Resolved"
        ?
        ?
[Stage 2: Quality Gate Audit]
System evaluates 6 strict completeness and validation criteria
        ??? If FAILED ??> Displays blocking reasons to developer (Promotion Disabled)
        ?
        ??? If PASSED ??> Enables Promotion Action
                 ?
                 ?
[Stage 3: Vectorization & Upsert]
Generates semantic chunks -> Encodes 384-d vectors -> Atomic upsert into ChromaDB
                 ?
                 ?
[Stage 4: Relational Synchronization]
HistoricalDefect record committed to SQLite -> Bug flagged indexed_in_kb = True
```

### 12.3 Quality Gate & 6 Validation Criteria
To prevent low-quality, noisy, or duplicate data from degrading retrieval precision, all candidates must satisfy the six validation criteria evaluated in `KBGrowthService.check_quality_gate()` ([`backend/app/services/kb_growth_service.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/services/kb_growth_service.py)):

| # | Quality Gate Criterion | Evaluation Rule | Blocking Condition | Rationale |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Defect Description Completeness** | $	ext{Title} \ge 5	ext{ chars} \land 	ext{Description} \ge 15	ext{ chars}$ | **Fails** if title or description is missing or too short | Ensures sufficient textual content for embedding generation |
| **2** | **Architectural Component** | Component specified and not `'General'` | **Warning** if generic component | Ensures accurate domain-specific filtering |
| **3** | **Error Logs & Trace Context** | $	ext{Stack Trace} > 15	ext{ chars} \lor 	ext{Error Logs} > 10	ext{ chars}$ | **Fails** if both stack trace and error logs are empty | Prevents indexing defects that lack technical failure signatures |
| **4** | **Root Cause Grounding** | Diagnosis contains root cause or resolution notes explain cause | **Warning** if causal mechanism is unspecified | Guarantees downstream root cause agents can cite the precedent |
| **5** | **Confirmed Resolution & Fix** | Resolution notes $\ge 10	ext{ chars}$ | **Fails** if resolution notes are missing or empty | Ensures the knowledge base only stores actionable, verified solutions |
| **6** | **Indexing Idempotency** | `bug.indexed_in_kb == False` | **Fails** if defect has already been promoted | Prevents duplicate vector chunk insertion and data bloat |

### 12.4 Incremental Vectorization & Non-Disruptive Upsert
When promotion executes via `POST /api/knowledge-base/growth/promote/{bug_id}`:
1. **Semantic Chunking**: The defect is processed using `chunk_historical_bug()`. Three dedicated chunks are created:
   - Header & Description chunk.
   - Stack trace & Error log chunk.
   - Root cause & Resolution fix chunk.
2. **Dense Vectorization**: `EmbeddingService.get_embeddings()` encodes each chunk into a 384-dimensional unit vector using `sentence-transformers/all-MiniLM-L6-v2`.
3. **Atomic Non-Disruptive Upsert**: Vectors are added to the existing `historical_defects` ChromaDB collection via `VectorStore.add_chunks()`. Because ChromaDB utilizes `collection.upsert()`, existing baseline records (Mozilla, Apache, Eclipse) remain intact without service interruption or index rebuilds.
4. **Relational Synchronization**: A new `HistoricalDefect` row is inserted into SQLite with `dataset_source="Platform"`, `bug_id=str(bug.id)[:8]`, and a link to the original bug report.

### 12.5 Audit Logging & Traceability
Promoted records maintain complete traceability:
- Every chunk metadata object preserves the original platform `bug_id`, `source="Platform"`, `project="Platform User Submissions"`, and creation timestamp.
- The `BugReport` table marks `indexed_in_kb = True` and records `resolved_at = datetime.utcnow()`.
- The audit trail ensures that administrators can review, trace, or remove any promoted record if necessary.

### 12.6 Source Code & Implementation Files
- **Service Logic**: [`backend/app/services/kb_growth_service.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/services/kb_growth_service.py)
- **API Controller**: [`backend/app/api/kb_growth.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/api/kb_growth.py)
- **Pydantic Schemas**: [`backend/app/schemas/growth.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/schemas/growth.py)
- **Frontend Promotion Component**: [`frontend/src/components/growth/ResolutionPromotionCard.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/components/growth/ResolutionPromotionCard.jsx)
- **Frontend Growth Page**: [`frontend/src/pages/KnowledgeBasePage.jsx`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/frontend/src/pages/KnowledgeBasePage.jsx) (Growth Tab)

---
"""

SECTION_13 = """# Section 13 — REST API Catalog (Complete 24 Endpoints)

The platform backend exposes a total of 24 fully documented REST API endpoints across six modular controllers. All endpoints return standardized JSON responses and include Swagger / OpenAPI documentation accessible at `/docs`.

### 13.1 Authentication Controller (`/api/auth`)
- **Controller File**: [`backend/app/api/auth.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/api/auth.py)

| HTTP Method | Endpoint URI | Auth Required? | Request Payload | Response Schema | Description & Purpose |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | No | `UserCreate` (email, username, password) | `UserResponse` | Registers a new developer account with bcrypt-hashed credentials |
| `POST` | `/api/auth/login` | No | `OAuth2PasswordRequestForm` (username, password) | `Token` (access_token, token_type) | Authenticates credentials and returns a signed 60-minute JWT token |
| `GET` | `/api/auth/me` | **Yes** (Bearer) | None | `UserResponse` | Fetches the authenticated developer profile and permissions |

### 13.2 Bug Management Controller (`/api/bugs` and `/bugs`)
- **Controller File**: [`backend/app/api/bugs.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/api/bugs.py)

| HTTP Method | Endpoint URI | Auth Required? | Request Payload | Response Schema | Description & Purpose |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `POST` | `/api/bugs` | **Yes** (Bearer) | `BugCreate` (title, desc, stack_trace, logs, component) | `BugResponse` (HTTP 201) | Creates a new software defect submission |
| `POST` | `/api/bugs/upload` | **Yes** (Bearer) | `multipart/form-data` (`file`: `.log` or `.txt`) | `BugUploadResponse` | Ingests and heuristically parses raw crash log files up to 10MB |
| `GET` | `/api/bugs` | **Yes** (Bearer) | Query: `skip`, `limit`, `user_only` | `List[BugResponse]` | Lists bug reports submitted by user or across platform |
| `GET` | `/api/bugs/stats/summary`| **Yes** (Bearer) | None | JSON summary counts | Returns total bugs, diagnosed bugs, and pending counts |
| `GET` | `/api/bugs/{bug_id}` | **Yes** (Bearer) | Path: `bug_id` | `BugResponse` | Fetches single defect record details |
| `POST` | `/api/bugs/{bug_id}/analyze` | **Yes** (Bearer) | Path: `bug_id` | `DiagnosisResponse` | **Triggers the 5-Agent Diagnostic Orchestration Pipeline** |
| `GET` | `/api/bugs/{bug_id}/diagnosis` | **Yes** (Bearer) | Path: `bug_id` | `DiagnosisResponse` | Retrieves saved 7-section diagnosis findings |

### 13.3 Knowledge Base Controller (`/api/knowledge-base`)
- **Controller File**: [`backend/app/api/knowledge_base.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/api/knowledge_base.py)

| HTTP Method | Endpoint URI | Auth Required? | Request Payload | Response Schema | Description & Purpose |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `GET` | `/api/knowledge-base/defects` | No | Query: `source`, `project`, `component`, `skip`, `limit` | `List[HistoricalDefectResponse]` | Lists curated historical defects with multi-source filtering |
| `POST` | `/api/knowledge-base/search` | No | `SemanticSearchRequest` (query, top_k, source) | `SemanticSearchResponse` | Executes direct semantic vector search against ChromaDB |
| `GET` | `/api/knowledge-base/stats` | No | None | JSON stats object | Returns indexed defect counts per source (Mozilla, Apache, Eclipse, Platform) |

### 13.4 Knowledge Base Growth Controller (`/api/knowledge-base/growth`)
- **Controller File**: [`backend/app/api/kb_growth.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/api/kb_growth.py)

| HTTP Method | Endpoint URI | Auth Required? | Request Payload | Response Schema | Description & Purpose |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `POST` | `/api/knowledge-base/growth/resolve/{id}` | Optional | `ResolutionSubmission` (notes, fix_code) | JSON status confirmation | Marks bug as resolved with verified fix code |
| `GET` | `/api/knowledge-base/growth/validate/{id}` | Optional | Path: `bug_id` | `QualityGateCheckResult` | Audits defect against the 6 Quality Gate criteria |
| `POST` | `/api/knowledge-base/growth/promote/{id}` | Optional | Optional `ResolutionSubmission` | `PromotionResponse` | Promotes approved defect into ChromaDB vector knowledge base |
| `GET` | `/api/knowledge-base/growth/candidates` | Optional | None | `List[GrowthCandidateItem]` | Lists all defects with Quality Gate eligibility status |
| `GET` | `/api/knowledge-base/growth/stats` | Optional | None | `KnowledgeBaseGrowthStats` | Returns growth metrics (total promoted, pass rate, active candidates) |

### 13.5 Defect Pattern Analytics Controller (`/api/analytics`)
- **Controller File**: [`backend/app/api/analytics.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/api/analytics.py)

| HTTP Method | Endpoint URI | Auth Required? | Request Payload | Response Schema | Description & Purpose |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `GET` | `/api/analytics/overview` | Optional | Query: filters (component, severity, date) | `AnalyticsOverviewResponse` | Returns comprehensive analytical KPIs, hotspots, clusters, and trends |
| `GET` | `/api/analytics/components` | Optional | Query: `source` ('all', 'submitted', 'historical') | `List[ComponentHotspot]` | Returns component defect rankings and failure densities |
| `GET` | `/api/analytics/exceptions` | Optional | Query: `component`, `source` | `List[ExceptionPattern]` | Returns recurring exception signatures and failure points |
| `GET` | `/api/analytics/root-causes` | Optional | Query: `component`, `source` | `List[RootCauseTheme]` | Returns root cause themes mapped to remediation patterns |
| `GET` | `/api/analytics/clusters` | Optional | Query: `component`, `source` | `List[SemanticCluster]` | Returns semantically clustered defect groups |
| `GET` | `/api/analytics/trends` | Optional | Query: `component`, `source` | `TimeTrendAnalysis` | Returns time-series defect velocity and frequency trends |
| `GET` | `/api/analytics/filters` | Optional | None | `AnalyticsFilterOptions` | Returns available filter dropdown values for the UI |

### 13.6 System Health Controller (`/`)
- **Controller File**: [`backend/app/api/health.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/api/health.py)

| HTTP Method | Endpoint URI | Auth Required? | Request Payload | Response Schema | Description & Purpose |
| :---: | :--- | :---: | :--- | :--- | :--- |
| `GET` | `/health` | No | None | JSON (`status: "healthy"`, timestamp) | System health-check endpoint for load balancers |
| `GET` | `/` | No | None | JSON (platform name, version, status) | Root API metadata and welcome endpoint |

---
"""

SECTION_14 = """# Section 14 — Authentication & Security Architecture

### 14.1 Authentication Mechanism
User identity and session verification are implemented in [`backend/app/api/auth.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/api/auth.py) using the **OAuth2 Password Bearer flow** with **JSON Web Tokens (JWT)**:
- **Token Format**: Standard RFC 7519 compact JWT string signed using the HMAC-SHA256 (`HS256`) cryptographic algorithm.
- **Token Lifetime**: Configured via `ACCESS_TOKEN_EXPIRE_MINUTES` (defaults to **60 minutes**).
- **Transport**: Transmitted in HTTP request headers using the standard `Authorization: Bearer <TOKEN>` header.
- **Payload Claims**:
  ```json
  {
    "sub": "engineer@company.com",
    "exp": 1727780400
  }
  ```

### 14.2 Password Hashing & Bcrypt
User credentials are protected using salted, adaptive cryptographic hashing:
- **Hashing Library**: `passlib.context.CryptContext` utilizing the `bcrypt` algorithm.
- **Work Factor**: Configured with automatic random salting and standard computational complexity rounds.
- **Security Rule**: Plaintext passwords are never persisted to disk or logged. At registration, `BugService` computes `pwd_context.hash(password)`. At login, `pwd_context.verify(plain_password, hashed_password)` executes in constant time to prevent timing side-channel attacks.

### 14.3 Protected Endpoints & Dependency Injection
FastAPI's dependency injection system guarantees strict endpoint authorization:
- **Strict Protection (`get_current_user`)**:
  - Enforced on bug creation, file uploads, listing user tickets, and triggering diagnoses.
  - Extracts the bearer token, verifies signature against `SECRET_KEY`, checks token expiration, and queries the `User` record in SQLite.
  - If invalid or expired, raises `HTTP 401 Unauthorized` with `WWW-Authenticate: Bearer` header.
- **Optional Identification (`get_current_user_optional`)**:
  - Utilized on analytical reporting, knowledge base search, and growth endpoints.
  - Allows public or cross-functional team viewing while capturing user identity when a session token is present.

### 14.4 Token Invalidation & Security Scope
- **Stateless Verification**: Tokens are verified cryptographically without database token lookup queries on every request, ensuring high backend throughput.
- **CORS Configuration**: Configured in [`backend/app/main.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/main.py) via `CORSMiddleware`, restricting allowed methods and headers while allowing frontend dev origin (`http://localhost:5173`).
- **SQL Injection Prevention**: All database access executes through SQLAlchemy ORM parameterized query abstractions, entirely preventing SQL injection vulnerabilities.
- **Pydantic Input Sanitization**: All endpoint inputs are strictly validated against Pydantic schemas, rejecting oversized or malformed payloads before business logic execution.

---
"""

print("Part 4 defined successfully.")
