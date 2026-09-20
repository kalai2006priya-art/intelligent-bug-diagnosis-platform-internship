# Agent Orchestration Specification

The multi-agent workflow coordinates five specialized agents across distinct execution stages, ensuring that downstream agents operate on validated, enriched context rather than isolated fragments.

---

## 1. Orchestration Pipeline Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Gateway as FastAPI Backend
    participant Store as SQLite Database
    participant Orchestrator as Agent Orchestrator
    participant Triage as Triage Agent
    participant LogAnalysis as Log Analysis Agent
    participant RAG as RAG / Vector Retriever
    participant RootCause as Root Cause Agent
    participant Duplicate as Duplicate Detection Agent
    participant Remediation as Remediation Agent

    User->>Gateway: POST /bugs/{bug_id}/analyze
    Gateway->>Store: Load BugReport
    Gateway->>Orchestrator: run_orchestration(bug_report)

    Note over Orchestrator,LogAnalysis: STAGE 1: Input Analysis & Triage
    par Run Triage & Log Analysis
        Orchestrator->>Triage: analyze(bug_report)
        Triage-->>Orchestrator: TriageResult
    and
        Orchestrator->>LogAnalysis: parse(bug_report.stack_trace, bug_report.error_logs)
        LogAnalysis-->>Orchestrator: LogAnalysisResult
    end

    Note over Orchestrator,RAG: STAGE 2: Historical Defect Retrieval
    Orchestrator->>RAG: retrieve_similar(query, top_k=5)
    RAG-->>Orchestrator: List[HistoricalDefectChunk]

    Note over Orchestrator,Duplicate: STAGE 3: Root Cause & Duplicate Detection
    par Run Root Cause & Duplicate Detection
        Orchestrator->>RootCause: infer_root_cause(bug, triage, log_analysis, rag_context)
        RootCause-->>Orchestrator: RootCauseResult
    and
        Orchestrator->>Duplicate: detect_duplicates(bug, rag_context)
        Duplicate-->>Orchestrator: DuplicateDetectionResult
    end

    Note over Orchestrator,Remediation: STAGE 4: Remediation Synthesis
    Orchestrator->>Remediation: recommend_fixes(triage, log_analysis, root_cause, duplicates)
    Remediation-->>Orchestrator: RemediationResult

    Note over Orchestrator,Gateway: STAGE 5: Consolidation & Persistence
    Orchestrator->>Store: Save AgentDiagnosis (structured JSON)
    Orchestrator-->>Gateway: Complete Diagnosis Object
    Gateway-->>User: HTTP 200 JSON Response
```

---

## 2. Stage Execution Details

### Stage 1: Input Analysis & Parsing
- **Inputs**: Raw bug report (title, description, optional stack trace, error logs, user-supplied component, environment).
- **Execution**:
  - `TriageAgent`: Assesses severity and priority; identifies likely system subsystem.
  - `LogAnalysisAgent`: Parses stack traces, extracts exception class, failure point (`file:line`), and reconstructs call hierarchy.
- **Output Artifacts**: `TriageResult` and `LogAnalysisResult`.

### Stage 2: Semantic RAG Retrieval
- **Query Synthesis**: The orchestrator builds an enriched query vector combining the bug title, failure point from Log Analysis, and core symptoms from Triage.
- **Vector Search**: ChromaDB retrieves the top-5 historical defect chunks from Mozilla, Apache, and Eclipse datasets.
- **Output Artifacts**: Structured collection of retrieved chunks with cosine similarities and resolution summaries.

### Stage 3: Root Cause & Duplicate Reasoning
- **Execution**:
  - `RootCauseAgent`: Synthesizes Stage 1 parser outputs with Stage 2 historical precedents. Generates a grounded hypothesis with citations.
  - `DuplicateDetectionAgent`: Compares similarity metrics against calibrated thresholds (`0.85` duplicate / `0.65` related) to classify issue duplication.
- **Output Artifacts**: `RootCauseResult` and `DuplicateDetectionResult`.

### Stage 4: Remediation Generation
- **Inputs**: All Stage 1, 2, and 3 outputs.
- **Execution**:
  - `RemediationAgent`: Produces targeted code snippets, configuration adjustments, and step-by-step verification procedures.
  - Categorizes evidence foundation: Historical Evidence vs. General Best Practice vs. Agent Recommendation.
- **Output Artifacts**: `RemediationResult`.

### Stage 5: Persistence & Serialization
- All agent outputs are committed atomically to SQLite in the `agent_diagnoses` table.
- Results are accessible via `GET /bugs/{bug_id}/diagnosis` and formatted for the interactive UI.

---

## 3. Resilience & Failure Isolation

1. **Agent Error Handling**: If an individual agent encounters an unexpected exception or formatting error, the orchestrator catches it, logs the trace, and inserts an `"Insufficient Evidence"` fallback state for that specific agent.
2. **Cascading Protection**: Downstream agents check upstream output statuses. If `LogAnalysisAgent` returns `"Insufficient Evidence"`, `RootCauseAgent` shifts focus to textual description heuristics rather than aborting the pipeline.
3. **Deterministic Heuristic Fallback**: If external LLM APIs (Gemini/OpenAI) are unavailable, unreachable, or unconfigured, the system automatically falls back to internal rule-based parsers, ensuring zero pipeline crashes.
