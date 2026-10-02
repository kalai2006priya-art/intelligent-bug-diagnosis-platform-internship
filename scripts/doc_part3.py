"""
Part 3 of M4.4 Technical Documentation:
Section 8, Section 9, Section 10
"""

SECTION_8 = """# Section 8 — Five Specialized Diagnostic Agents

### 8.1 Triage Agent
- **Source File**: [`backend/app/agents/triage_agent.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/agents/triage_agent.py)
- **Execution Stage**: Stage 1a (Parallel execution with Log Analysis Agent)

#### 8.1.1 Role & Objectives
The **Triage Agent** performs the automated assessment of newly submitted defect reports. It performs three critical triage functions:
1. **Severity Classification**: Determines technical impact on system stability (`Critical`, `High`, `Medium`, `Low`).
2. **Priority Assignment**: Recommends developer remediation urgency (`Critical`, `High`, `Medium`, `Low`).
3. **Affected Component Mapping**: Classifies the bug into one of seven core architectural subsystems.

#### 8.1.2 Inputs & Output Schema
- **Input Parameters**:
  - `title`: Short summary of the defect.
  - `description`: Detailed user narrative.
  - `stack_trace`: Raw execution frames (optional).
  - `error_logs`: Console or server error messages (optional).
  - `component`: User-provided component hint (optional).
  - `environment`: Host runtime environment (optional).
- **Pydantic Output Model (`TriageResult`)**:
  ```python
  class TriageResult(BaseModel):
      severity: str           # 'Critical' | 'High' | 'Medium' | 'Low'
      priority: str           # 'Critical' | 'High' | 'Medium' | 'Low'
      affected_component: str # Subsystem name
      confidence: float       # 0.0 to 1.0
      reasoning: str          # Observable natural language rationale
  ```

#### 8.1.3 Rule Heuristics & Decision Logic
The agent executes a deterministic heuristic engine:
- **Insufficient Evidence Check**: If the combined text contains fewer than 35 characters and lacks logs, the agent flags the report:
  - Severity: `Low`, Priority: `Low`, Confidence: `0.30`
  - Reasoning: `"Insufficient Evidence: The bug report contains very little descriptive context or technical error logs to evaluate impact reliably."`
- **Architectural Component Heuristics**:
  - *Memory & Runtime Resources*: Matches keywords `["memory", "leak", "vram", "oom", "metaspace", "heap", "garbage"]`
  - *Authentication & Authorization*: Matches `["login", "auth", "token", "jwt", "password", "session", "credential", "cors"]`
  - *Database / Persistence*: Matches `["database", "sql", "postgres", "mysql", "sqlite", "query", "deadlock", "transaction", "pool", "connection"]`
  - *UI & Frontend Rendering*: Matches `["render", "canvas", "css", "button", "ui", "dom", "display", "widget", "frontend", "modal"]`
  - *Networking & API*: Matches `["http", "socket", "timeout", "network", "fetch", "rest", "api", "endpoint"]`
  - *Storage & File System*: Matches `["filenotfound", "filesystem", "disk", "s3", "storage", "ioerror", "directory"]`
  - *General / Core Subsystem*: Default fallback category.
- **Severity & Priority Heuristics**:
  - **Critical** (Confidence 0.93): Triggered by crash dumps, `fatal`, `out of memory`, `access_violation`, `segfault`, `system down`, `data corruption`, `infinite loop`.
  - **High** (Confidence 0.89): Triggered by `nullpointerexception`, `npe`, `blocked`, `cannot login`, `fails completely`, `deadlock`, `timeout`, `connection refused`.
  - **Low** (Confidence 0.82): Triggered by `slow`, `glitch`, `format`, `alignment`, `warning`, `typo`, `cosmetic`.
  - **Medium** (Confidence 0.85): Standard functional defects without catastrophic downtime.

#### 8.1.4 Observable Reasoning & Error Handling
The agent returns human-readable justification connecting matched tokens to its classification decisions. If an internal exception occurs, a defensive fallback assigns `Medium`/`Medium`, preserves user component hints, sets confidence to `0.30`, and logs the error without aborting downstream agents.

---

### 8.2 Log Analysis Agent
- **Source File**: [`backend/app/agents/log_analysis_agent.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/agents/log_analysis_agent.py)
- **Parser Utilities**: [`backend/app/utils/parsers.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/utils/parsers.py)
- **Execution Stage**: Stage 1b (Parallel execution with Triage Agent)

#### 8.2.1 Role & Objectives
The **Log Analysis Agent** parses execution stack traces and console logs across multiple programming languages. It isolates:
1. Exact exception or error class name.
2. Root failure point (`filename:line_number`).
3. Calling path (stack frame execution hierarchy).
4. Primary error message string.

#### 8.2.2 Inputs & Output Schema
- **Input Parameters**: `stack_trace`, `error_logs`, `description`.
- **Pydantic Output Model (`LogAnalysisResult`)**:
  ```python
  class LogAnalysisResult(BaseModel):
      status: str                             # 'Success' | 'Insufficient Evidence'
      exception_type: Optional[str] = None     # e.g., 'NullPointerException'
      error_message: Optional[str] = None      # e.g., 'division by zero'
      failure_point: Optional[str] = None      # e.g., 'AuthService.java:55'
      affected_code_path: Optional[str] = None # e.g., 'Controller -> Service -> DAO'
      confidence: float                       # 0.0 to 1.0
  ```

#### 8.2.3 Multi-Language Parsing Heuristics
The parsing engine in `parsers.py` supports four major stack frame conventions:
- **Java / JVM Stacks**:
  - Exception regex: `r'([a-zA-Z0-9_.]+(?:Exception|Error|Throwable))(?::\s*(.*))?'`
  - Frame regex: `r'at\s+([a-zA-Z0-9_$.]+)\.([a-zA-Z0-9_$]+)\(([^:]+):(\d+)\)'`
  - Captures class, method, filename, and line number.
- **Python Tracebacks**:
  - Header regex: `r'Traceback \(most recent call last\):'`
  - Frame regex: `r'File "([^"]+)", line (\d+), in (\w+)'`
  - Exception regex: `r'^([A-Z][a-zA-Z0-9_]*(?:Error|Exception)): (.*)$'`
- **C / C++ Native Crash Dumps**:
  - Crash signature regex: `r'Crash\s*\[@\s*([^\]]+)\]'`
  - Stack frame regex: `r'^\d+\s+([a-zA-Z0-9_\.]+)!(?:([a-zA-Z0-9_:]+))\s*\[(.*):(\d+)\]'`
- **JavaScript / Node.js Errors**:
  - Exception regex: `r'^([a-zA-Z_$][a-zA-Z0-9_$]*(?:Error|Exception)):\s*(.*)$'`
  - Frame regex: `r'at\s+(?:([a-zA-Z0-9_$<>.]+)\s+\()?([^:]+):(\d+):(\d+)\)?'`

#### 8.2.4 Insufficient Evidence Handling
If the submission does not include stack frames or error logs (or if content is under 10 characters), the agent gracefully sets:
- `status`: `"Insufficient Evidence"`
- `confidence`: `0.0`
- `failure_point`: `None`
- `error_message`: `"No stack trace or runtime error logs provided."`

---

### 8.3 Root Cause Agent
- **Source File**: [`backend/app/agents/root_cause_agent.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/agents/root_cause_agent.py)
- **Execution Stage**: Stage 3a (Consumes Stage 1 outputs + Stage 2 RAG retrieval results)

#### 8.3.1 Role & Objectives
The **Root Cause Agent** synthesizes empirical symptom data from Stage 1 with historical precedents retrieved via RAG in Stage 2. It isolates the underlying technical reason for defect manifestation.

#### 8.3.2 Inputs & Output Schema
- **Input Parameters**: `bug_description`, `triage_output`, `log_analysis_output`, `retrieved_defects`.
- **Pydantic Output Model (`RootCauseResult`)**:
  ```python
  class RootCauseEvidenceItem(BaseModel):
      bug_id: str
      source: str
      similarity: float
      evidence: str

  class RootCauseResult(BaseModel):
      status: str                                             # 'Supported' | 'Insufficient Evidence'
      root_cause_hypothesis: str                             # Probable cause
      confidence: float                                       # 0.0 to 1.0
      supporting_evidence: List[RootCauseEvidenceItem] = []   # Empirical precedents
      reasoning: str                                          # Deductive causal logic
  ```

#### 8.3.3 Separation of Evidence and Hypothesis
To ensure technical integrity and audit compliance, the agent strictly demarcates **Empirical Supporting Evidence** from **Agent Reasoning**:
- **Supporting Evidence**: Formed exclusively from retrieved historical defects with similarity $S > 0.40$. Each record displays the historical `bug_id`, repository `source`, semantic `similarity`, and documented resolution excerpt.
- **Root Cause Hypothesis**: Formulates the probable causal mechanism (e.g., missing null safety checks, unhandled division edge cases, memory lifecycle mismanagement).
- **Agent Reasoning**: Explains how the historical precedent applies to the current defect's specific failure point.

---

### 8.4 Duplicate Detection Agent
- **Source File**: [`backend/app/agents/duplicate_detection_agent.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/agents/duplicate_detection_agent.py)
- **Execution Stage**: Stage 3b (Consumes Stage 2 RAG retrieval + active platform bug records)

#### 8.4.1 Role & Objectives
The **Duplicate Detection Agent** cross-references the submitted defect against:
1. Curated historical defects in the ChromaDB vector database.
2. Active defects previously submitted by developers on the platform.

Its objective is to eliminate redundant triage cycles and prevent duplicate ticket accumulation.

#### 8.4.2 Inputs & Output Schema
- **Input Parameters**: `bug_title`, `bug_description`, `retrieved_defects`, `submitted_matches`.
- **Pydantic Output Model (`DuplicateDetectionResult`)**:
  ```python
  class DuplicateMatchItem(BaseModel):
      bug_id: str
      similarity: float
      title: str
      source: str
      project: Optional[str] = None
      component: Optional[str] = None
      resolution_summary: Optional[str] = None

  class DuplicateDetectionResult(BaseModel):
      status: str                                    # 'Likely Duplicate' | 'Related Issue' | 'New / Unmatched' | 'Insufficient Evidence'
      matches: List[DuplicateMatchItem] = []         # Candidates >= 0.65 similarity
      reasoning: str                                 # Explanation with top similarity score
  ```

#### 8.4.3 Multi-Source Candidate Aggregation
The agent builds a combined candidate pool from both vector search results and database queries:
1. Vector candidates are mapped from ChromaDB chunk metadata (`bug_id`, `source`, `project`, `component`, `resolution`).
2. Platform candidates are retrieved from SQLite (`BugReport.query`), comparing titles and descriptions.
3. All candidates are merged and sorted in descending order by similarity score $S$.
4. Candidates with $S \ge 0.65$ are retained (up to the top 5 matches).

---

### 8.5 Remediation Agent
- **Source File**: [`backend/app/agents/remediation_agent.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/agents/remediation_agent.py)
- **Execution Stage**: Stage 4 (Consumes Stage 1, Stage 2, and Stage 3 outputs)

#### 8.5.1 Role & Objectives
The **Remediation Agent** translates root cause findings and historical precedents into concrete, actionable engineering solutions. It produces copy-pasteable code patches and step-by-step test verification plans.

#### 8.5.2 Inputs & Output Schema
- **Input Parameters**: `triage_output`, `log_analysis_output`, `root_cause_output`, `duplicate_output`.
- **Pydantic Output Model (`RemediationResult`)**:
  ```python
  class RecommendationItem(BaseModel):
      recommendation: str
      confidence: float
      basis: str                     # 'Historical Evidence' | 'General Best Practice' | 'Agent Recommendation'
      affected_module: Optional[str] = None
      suggested_code: Optional[str] = None
      supporting_bug_ids: List[str] = []
      validation_steps: List[str] = []

  class RemediationResult(BaseModel):
      status: str                                    # 'Supported' | 'Insufficient Evidence'
      recommendations: List[RecommendationItem] = []
      general_guidance: Optional[str] = None
  ```

#### 8.5.3 Three-Tier Basis Classification
Every recommendation is tagged with an explicit provenance classification:
1. **`Historical Evidence`**: The recommendation is derived directly from an accepted patch in an existing historical bug report (e.g., Mozilla, Apache, Eclipse). Linked `supporting_bug_ids` verify this grounding.
2. **`General Best Practice`**: The recommendation implements established industry standard design patterns (e.g., connection pool sizing, exponential backoff, resource try-with-resources).
3. **`Agent Recommendation`**: Synthesized heuristic logic targeting the specific failure point isolated by the Log Analysis Agent.

#### 8.5.4 Actionable Code Snippets & Verification Plans
Each recommendation delivers:
- **Code Block**: Syntactically valid code snippets demonstrating defensive guards, null-coalescing operations, boundary checks, or retry loops.
- **Validation Checklist**: Step-by-step QA instructions (e.g., "Unit test with null payload", "Stress-test under 100 concurrent workers", "Verify connection pool metrics in Prometheus").

---

### 8.6 Comparative Agent Architecture Matrix

The following matrix summarizes the technical contracts, runtime roles, and fail-safe designs across all five specialized diagnostic agents:

| Agent Name | Execution Stage | Primary Input Sources | Core Analysis & Heuristics | Primary Output Schema | Fallback Mechanism |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Triage Agent** | Stage 1a | Title, Description, Component, Logs | Keyword domain dictionaries, severity indicators, length heuristics | `TriageResult` (Severity, Priority, Component, Confidence) | Defaults to `Medium`/`Medium`, `0.30` confidence, preserves component hints |
| **Log Analysis Agent** | Stage 1b | Stack Trace, Error Logs, Description | Regex stack frame extractors (Java, Python, C++, JS, SQL) | `LogAnalysisResult` (Exception, Failure Point, Code Path) | Returns `Insufficient Evidence`, `0.0` confidence |
| **Root Cause Agent** | Stage 3a | Stage 1 findings, Top-5 RAG Defect Chunks | Causal synthesis, historical precedent matching ($S > 0.40$) | `RootCauseResult` (Hypothesis, Supporting Evidence, Reasoning) | Separates evidence from hypothesis; flags `Insufficient Evidence` if weak |
| **Duplicate Detection Agent** | Stage 3b | RAG matches, Submitted platform bugs | 3-tier cosine threshold evaluation ($\ge 0.85$, $\ge 0.65$, $< 0.65$) | `DuplicateDetectionResult` (Status, Ranked Matches, Reasoning) | Returns `New / Unmatched` if similarity is below threshold |
| **Remediation Agent** | Stage 4 | All Stage 1?3 outputs, Historical Bug IDs | Provenance tagging (`Historical`, `Best Practice`, `Agent`), code synthesis | `RemediationResult` (Code Snippets, Basis, Validation Steps) | Flags `Insufficient Evidence` if root cause is unsupported |

---
"""

SECTION_9 = """# Section 9 — Multi-Agent Orchestration Pipeline

### 9.1 Orchestration Workflow & Execution Graph
The coordination of all diagnostic sub-agents is handled centrally by the `AgentOrchestrator` class located at [`backend/app/agents/orchestrator.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/agents/orchestrator.py). 

The orchestration pipeline executes according to a staged sequence designed to minimize latency and ensure that downstream reasoning agents always receive clean, validated input context:

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / Client
    participant API as FastAPI Router (/bugs/{id}/analyze)
    participant Orch as AgentOrchestrator
    participant Triage as Triage Agent (1a)
    participant LogAg as Log Analysis Agent (1b)
    participant RAG as RAGRetriever & ChromaDB
    participant RCA as Root Cause Agent (3a)
    participant DupA as Duplicate Detection Agent (3b)
    participant RemA as Remediation Agent (4)
    participant DB as SQLite (agent_diagnoses)

    Dev->>API: POST /api/bugs/{id}/analyze
    API->>Orch: run_pipeline(db, bug)
    Note over Orch: Set bug.status = "Analyzing"

    par Stage 1: Initial Ingestion & Triage
        Orch->>Triage: analyze(title, desc, stack_trace, logs)
        Orch->>LogAg: analyze(stack_trace, logs, desc)
    end
    Triage-->>Orch: TriageResult (Severity, Component, Conf)
    LogAg-->>Orch: LogAnalysisResult (Exception, Failure Point)

    Note over Orch: Construct RAG Query from Title + Exception + Failure Point
    Orch->>RAG: retrieve_similar_defects(query, top_k=5)
    RAG-->>Orch: List of 5 Historical Defect Chunks

    par Stage 3: Evidence Synthesis & Deduplication
        Orch->>RCA: analyze(desc, triage_res, log_res, rag_chunks)
        Orch->>DupA: analyze(title, desc, rag_chunks, submitted_bugs)
    end
    RCA-->>Orch: RootCauseResult (Hypothesis, Supporting Evidence)
    DupA-->>Orch: DuplicateDetectionResult (Status, Top Matches)

    Note over Orch: Stage 4: Remediation Synthesis
    Orch->>RemA: analyze(triage_res, log_res, rca_res, dupa_res)
    RemA-->>Orch: RemediationResult (Code Fixes, Validation Steps)

    Note over Orch: Aggregate Confidence Score & Commit
    Orch->>DB: Upsert AgentDiagnosis record (JSON blobs)
    Orch->>DB: Set bug.status = "Diagnosed", commit()
    Orch-->>API: Return complete DiagnosisResponse
    API-->>Dev: HTTP 200 (Diagnosis JSON)
```

### 9.2 Staged Execution Flow

1. **Stage 1: Ingestion & Surface Analysis (Parallel)**:
   - `TriageAgent.analyze()` and `LogAnalysisAgent.analyze()` execute concurrently.
   - Triage determines business priority, severity, and component domain.
   - Log Analysis extracts the technical failure signature (`ExceptionType` and `failure_point`).
2. **Stage 2: RAG Semantic Context Retrieval**:
   - The orchestrator synthesizes an enriched query:
     `Query = bug.title + " " + exception_type + " " + failure_point + " " + bug.description[:200]`
   - Dense vector retrieval retrieves the top 5 semantically related historical chunks from ChromaDB.
3. **Stage 3: Evidence Synthesis & Deduplication (Parallel)**:
   - `RootCauseAgent` consumes Stage 1 findings and RAG defect chunks to formulate the root cause hypothesis.
   - `DuplicateDetectionAgent` checks retrieved historical chunks and active platform bug reports against similarity thresholds.
4. **Stage 4: Actionable Remediation Synthesis**:
   - `RemediationAgent` consumes all accumulated findings to assemble fix recommendations with code patches and validation checklists.
5. **Stage 5: Atomic Persistence & State Transition**:
   - Findings are serialized as JSON blobs into `agent_diagnoses`.
   - The parent bug's status updates from `"Analyzing"` to `"Diagnosed"`.
   - If the user omitted a component, the Triage Agent's classified component is backfilled onto the `BugReport` record.

### 9.3 Exception Isolation & Fault Tolerance
A primary design requirement of the orchestrator is defensive fault isolation. In enterprise environments, bug logs may contain corrupted binary data, unsupported formats, or null values. 

To prevent whole-pipeline crashes:
- Every agent invocation is wrapped in an independent `try-except` block.
- If an agent raises an exception, the orchestrator catches it, logs the full stack trace with `logger.error()`, and injects a valid fallback dictionary adhering to the expected Pydantic schema with `status="Insufficient Evidence"`.
- Subsequent agents can still proceed using whatever partial context is available.
- The pipeline guarantees that a valid `AgentDiagnosis` record is always generated and saved.

### 9.4 Overall Confidence Calculation
The overall confidence score of the diagnosis is an aggregated metric computed across the three primary analytical agents:

$$\text{Confidence}_{\text{overall}} = \text{round}\left( \frac{\text{Confidence}_{\text{triage}} + \text{Confidence}_{\text{log\_analysis}} + \text{Confidence}_{\text{root\_cause}}}{3.0}, \; 2 \right)$$

#### Rationale for Weighting:
- **Triage Confidence** reflects descriptive clarity and keyword relevance.
- **Log Analysis Confidence** reflects whether a concrete stack frame and root exception were successfully parsed.
- **Root Cause Confidence** reflects the degree of empirical support provided by historical precedents.
- A high overall confidence score ($\ge 0.85$) indicates that the defect is backed by clear stack traces, definite severity classification, and strong historical precedent.

---
"""

SECTION_10 = """# Section 10 — Semantic Similarity & Duplicate Detection Engine

### 10.1 Vector Representation & Embedding Model
Defect deduplication and semantic retrieval rely on dense vector embeddings generated by the `sentence-transformers/all-MiniLM-L6-v2` neural model:
- **Architecture**: 6-layer MiniLM Transformer.
- **Dimensionality**: **384 dense floating-point values**.
- **Vector Space Normalization**: Unit-length normalized such that $\|\mathbf{v}\|_2 = 1.0$.
- **Storage**: Indexed in ChromaDB under the `historical_defects` collection using an HNSW index graph.

### 10.2 Cosine Similarity Mathematical Formulation
For any two defect representations $\mathbf{u}$ and $\mathbf{v}$ embedded in 384-dimensional space, the Cosine Similarity is given by the inner product of the unit vectors:

$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \sum_{i=1}^{384} u_i \cdot v_i$$

ChromaDB computes Cosine Distance ($D_{\text{cos}}$) according to:
$$D_{\text{cos}}(\mathbf{u}, \mathbf{v}) = 1.0 - \text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) \in [0.0, 2.0]$$

To provide an intuitive, normalized score for developers and UI badges, the platform's `RAGRetriever` maps distance to a normalized similarity metric $S \in [0.0, 1.0]$:

$$S = 1.0 - \frac{D_{\text{cos}}}{2.0}$$

When two defect texts are semantically identical, $D_{\text{cos}} \to 0$ and $S \to 1.00$.

### 10.3 Three-Tier Threshold Classification Logic
The platform implements a three-tier classification scheme configured in [`backend/app/config.py`](file:///C:/Users/HP/Desktop/intelligent-bug-diagnosis-platform-internship/backend/app/config.py):

```python
SIMILARITY_THRESHOLD_DUPLICATE: float = 0.85  # Configurable threshold for duplicates
SIMILARITY_THRESHOLD_RELATED: float = 0.65    # Configurable threshold for related issues
```

The table below defines the operational interpretation and platform actions for each tier:

| Similarity Score ($S$) | Classification Status | UI Status Badge | Diagnostic Interpretation & Platform Action |
| :---: | :---: | :---: | :--- |
| **$S \ge 0.85$** | **Likely Duplicate** | ?? Red Badge | **Defect is nearly identical** to an existing bug. Shares the same failure point, exception type, and stack frames. Developers are prompted to review the linked bug before opening a new investigation. |
| **$0.65 \le S < 0.85$** | **Related Issue** | ?? Yellow Badge | **Defect shares structural or architectural commonality**. Affects the same subsystem, shares failure mechanisms, or exhibits similar symptom descriptions. Used as supporting context for root cause analysis. |
| **$S < 0.65$** | **New / Unmatched** | ?? Green Badge | **Defect is unique and novel**. No historical or platform bug meets the similarity threshold. Treated as an independent defect requiring full de-novo investigation. |

### 10.4 Duplicate Ranking & Deduplication Strategy
When evaluating duplicate candidates:
1. **Candidate Pool Synthesis**: The agent queries both the historical vector index ($k=5$) and recently submitted platform defects ($N=10$).
2. **Filtering**: Any candidate with similarity score $S < 0.65$ is excluded from the match list to prevent false positive alert fatigue.
3. **Descending Ranking**: Retained candidates are sorted descending by $S$.
4. **Status Determination**: The status of the report is determined by the highest-scoring candidate:
   - If $\max(S) \ge 0.85$, status is `"Likely Duplicate"`.
   - If $0.65 \le \max(S) < 0.85$, status is `"Related Issue"`.
   - Otherwise, status is `"New / Unmatched"`.
5. **UI Transparency**: Every match presented in the findings card displays the target `bug_id`, source repository, exact percentage similarity, issue title, and resolution status.

---
"""

print("Part 3 defined successfully.")
