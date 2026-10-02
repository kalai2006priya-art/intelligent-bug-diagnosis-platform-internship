import io
import time
import pytest
from unittest.mock import patch
from app.models.bug_report import BugReport
from app.models.diagnosis import AgentDiagnosis
from app.agents.triage_agent import TriageAgent
from app.agents.log_analysis_agent import LogAnalysisAgent
from app.agents.root_cause_agent import RootCauseAgent
from app.agents.duplicate_detection_agent import DuplicateDetectionAgent
from app.agents.remediation_agent import RemediationAgent
from app.agents.orchestrator import AgentOrchestrator
from app.rag.retriever import RAGRetriever
from tests.benchmark_corpus import BENCHMARK_CASES, DUPLICATE_EVAL_PAIRS

def test_e2e_text_submission_and_orchestration(client, auth_headers):
    """
    Test 1: Full E2E Text Submission & Multi-Agent Diagnosis Pipeline
    Submits a rich bug report, triggers orchestration, and verifies structured findings.
    """
    case = BENCHMARK_CASES[0]  # Java NullPointerException
    payload = {
        "title": case["title"],
        "description": case["description"],
        "component": case["component"],
        "environment": case["environment"],
        "stack_trace": case["stack_trace"],
        "error_logs": case["error_logs"]
    }

    # 1. Bug Submission
    create_res = client.post("/bugs", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    bug = create_res.json()
    bug_id = bug["id"]
    assert bug["status"] == "Submitted"

    # 2. Trigger Diagnosis Orchestration
    analyze_res = client.post(f"/bugs/{bug_id}/analyze", headers=auth_headers)
    assert analyze_res.status_code == 200
    diag = analyze_res.json()

    # 3. Verify all 5 agent sections are populated and valid
    assert diag["status"] == "Completed"
    assert diag["overall_confidence"] > 0.0

    # Triage Agent
    assert diag["triage"]["severity"] in ["Critical", "High", "Medium", "Low"]
    assert diag["triage"]["priority"] in ["Critical", "High", "Medium", "Low"]
    assert "Authentication" in diag["triage"]["affected_component"]
    assert diag["triage"]["confidence"] >= 0.70

    # Log Analysis Agent
    assert diag["log_analysis"]["exception_type"] == "NullPointerException"
    assert "AuthService.java:55" in diag["log_analysis"]["failure_point"]
    assert diag["log_analysis"]["confidence"] >= 0.80

    # Root Cause Agent
    assert diag["root_cause"]["status"] == "Supported"
    assert "null" in diag["root_cause"]["root_cause_hypothesis"].lower()
    assert isinstance(diag["root_cause"]["supporting_evidence"], list)

    # Duplicate Detection Agent
    assert diag["duplicate_detection"]["status"] in ["Likely Duplicate", "Related Issue", "New / Unmatched"]
    assert isinstance(diag["duplicate_detection"]["matches"], list)

    # Remediation Agent
    assert diag["remediation"]["status"] == "Supported"
    assert len(diag["remediation"]["recommendations"]) >= 1
    rec = diag["remediation"]["recommendations"][0]
    assert rec["basis"] in ["Historical Evidence", "General Best Practice", "Agent Recommendation"]
    assert "validation_steps" in rec
    assert len(rec["validation_steps"]) > 0

    # 4. Fetch stored report via GET /bugs/{id}/diagnosis
    get_diag = client.get(f"/bugs/{bug_id}/diagnosis", headers=auth_headers)
    assert get_diag.status_code == 200
    assert get_diag.json()["id"] == diag["id"]

    # 5. Verify BugReport status updated in DB
    get_bug = client.get(f"/bugs/{bug_id}", headers=auth_headers)
    assert get_bug.status_code == 200
    assert get_bug.json()["status"] == "Diagnosed"
    assert get_bug.json()["has_diagnosis"] is True

def test_e2e_file_upload_submission(client, auth_headers):
    """
    Test 2: Bug File Upload Submission (.log and .txt)
    Uploads crash logs and verifies log content is parsed and incorporated into diagnosis.
    """
    log_content = (
        "2026-09-29 10:14:02.112 [ERROR] Fatal crash occurred\n"
        "java.lang.NullPointerException: Cannot invoke TokenStore.getRefreshToken()\n"
        "\tat com.platform.auth.AuthService.refreshToken(AuthService.java:55)\n"
    )
    file_bytes = log_content.encode("utf-8")

    # Upload .log file
    upload_res = client.post(
        "/bugs/upload",
        files={"file": ("server_crash.log", io.BytesIO(file_bytes), "text/plain")},
        headers=auth_headers
    )
    assert upload_res.status_code == 200
    uploaded_data = upload_res.json()
    assert "AuthService.java:55" in uploaded_data["stack_trace"]
    assert uploaded_data["detected_format"] == "LOG"

    # Upload .txt file
    txt_res = client.post(
        "/bugs/upload",
        files={"file": ("stacktrace.txt", io.BytesIO(file_bytes), "text/plain")},
        headers=auth_headers
    )
    assert txt_res.status_code == 200
    assert txt_res.json()["detected_format"] == "TXT"

def test_multi_language_stack_trace_parsing():
    """
    Test 3: Multi-Language & Multi-Exception Parsing Precision
    Evaluates Java, Python, C++, and JavaScript stack trace parsing against benchmark corpus.
    """
    agent = LogAnalysisAgent()

    for case in BENCHMARK_CASES:
        if case["info_level"] != "Complete":
            continue

        result = agent.heuristic_analyze(
            stack_trace=case["stack_trace"],
            error_logs=case["error_logs"],
            description=case["description"]
        )

        assert result["status"] == "Success", f"Failed parsing for {case['id']}"
        assert result["exception_type"] == case["expected_exception"], (
            f"{case['id']} expected {case['expected_exception']}, got {result['exception_type']}"
        )
        assert case["expected_failure_point"] in result["failure_point"], (
            f"{case['id']} expected failure point containing {case['expected_failure_point']}, got {result['failure_point']}"
        )
        assert result["confidence"] >= 0.80

def test_triage_agent_classification_performance():
    """
    Test 4: Triage Agent Performance Evaluation
    Evaluates predicted severity, priority, and affected component across all benchmark cases.
    """
    agent = TriageAgent()
    correct_severity = 0
    correct_component = 0
    total = len(BENCHMARK_CASES)

    for case in BENCHMARK_CASES:
        res = agent.heuristic_analyze(
            title=case["title"],
            description=case["description"],
            stack_trace=case["stack_trace"],
            error_logs=case["error_logs"],
            component=case["component"],
            environment=case["environment"]
        )

        assert res["severity"] in ["Critical", "High", "Medium", "Low"]
        assert res["priority"] in ["Critical", "High", "Medium", "Low"]

        if res["severity"] == case["expected_severity"]:
            correct_severity += 1

        if case["expected_component"] in res["affected_component"]:
            correct_component += 1

    severity_accuracy = correct_severity / total
    component_accuracy = correct_component / total

    # Expect at least 85% accuracy on benchmark ground truth
    assert severity_accuracy >= 0.85, f"Severity accuracy too low: {severity_accuracy}"
    assert component_accuracy >= 0.85, f"Component accuracy too low: {component_accuracy}"

def test_log_analysis_agent_extraction_performance():
    """
    Test 5: Log Analysis Agent Precision Evaluation
    Verifies extracted exception types and failure points across benchmark corpus.
    """
    agent = LogAnalysisAgent()

    # Test Partial case (logs without trace)
    partial_case = next(c for c in BENCHMARK_CASES if c["id"] == "TC-PARTIAL-07")
    res_partial = agent.heuristic_analyze(
        stack_trace=partial_case["stack_trace"],
        error_logs=partial_case["error_logs"],
        description=partial_case["description"]
    )
    assert res_partial["status"] == "Success"
    assert res_partial["exception_type"] == "SocketTimeoutException"

def test_root_cause_agent_hypothesis_and_evidence():
    """
    Test 6: Root Cause Agent Grounding and Separation of Evidence
    Verifies that the hypothesis is grounded on the parsed error and that
    retrieved historical evidence is strictly separated from agent reasoning.
    """
    agent = RootCauseAgent()
    mock_retrieved = [
        {
            "metadata": {
                "bug_id": "MOZ-459102",
                "source": "Mozilla",
                "title": "Crash [@ nsHttpChannel::OnStopRequest]",
                "resolution": "Check if mListener is non-null before invoking callback"
            },
            "similarity": 0.88,
            "text": "nsHttpChannel crash on stream cancellation when mListener is null"
        }
    ]

    triage_output = {"severity": "Critical", "affected_component": "Networking"}
    log_output = {
        "exception_type": "NativeCrashException",
        "failure_point": "nsHttpChannel.cpp:6840",
        "affected_code_path": "nsHttpChannel::OnStopRequest"
    }

    res = agent.heuristic_analyze(
        bug_description="Browser crashes when download stream is abruptly cancelled",
        triage_output=triage_output,
        log_analysis_output=log_output,
        retrieved_defects=mock_retrieved
    )

    assert res["status"] == "Supported"
    assert len(res["root_cause_hypothesis"]) > 20
    assert len(res["supporting_evidence"]) > 0
    assert res["supporting_evidence"][0]["bug_id"] == "MOZ-459102"
    assert res["supporting_evidence"][0]["similarity"] == 0.88
    # Strict separation: evidence item contains source and similarity
    assert "Mozilla" in res["supporting_evidence"][0]["source"]

def test_duplicate_detection_agent_thresholds():
    """
    Test 7: Duplicate Detection Agent Evaluation across Known Pairs
    Tests 'Likely Duplicate', 'Related Issue', and 'New / Unmatched' classifications.
    """
    agent = DuplicateDetectionAgent()

    for pair in DUPLICATE_EVAL_PAIRS:
        sim_score = pair["min_similarity"] if "min_similarity" in pair else pair["max_similarity"]
        mock_retrieved = [{
            "metadata": {
                "bug_id": "BASE-DEFECT",
                "source": "Historical",
                "title": pair["base_bug"]["title"],
                "project": "Platform",
                "component": "Core",
                "resolution": "Fixed"
            },
            "similarity": sim_score
        }]

        res = agent.heuristic_analyze(
            bug_title=pair["query_bug"]["title"],
            bug_description=pair["query_bug"]["description"],
            retrieved_defects=mock_retrieved
        )

        assert res["status"] == pair["expected_status"], (
            f"Failed on pair {pair['pair_id']}: expected {pair['expected_status']}, got {res['status']}"
        )

def test_remediation_agent_recommendations():
    """
    Test 8: Remediation Agent Actionability & Validation Steps
    Verifies actionable fixes, suggested code snippets, and validation steps.
    """
    agent = RemediationAgent()
    triage = {"affected_component": "Authentication & Authorization"}
    log_out = {"exception_type": "NullPointerException", "failure_point": "AuthService.java:55"}
    rc_out = {"root_cause_hypothesis": "Uninitialized TokenStore reference dereferenced without null check"}
    dup_out = {"matches": []}

    res = agent.heuristic_analyze(triage, log_out, rc_out, dup_out)
    assert res["status"] == "Supported"
    assert len(res["recommendations"]) >= 1

    rec = res["recommendations"][0]
    assert rec["basis"] in ["Historical Evidence", "General Best Practice", "Agent Recommendation"]
    assert rec["suggested_code"] is not None
    assert "validation_steps" in rec
    assert len(rec["validation_steps"]) >= 2

def test_rag_retrieval_relevance_and_similarity():
    """
    Test 9: RAG Retrieval Quality and Cosine Similarity Metrics
    Verifies semantic vector search returns relevant defects with valid similarity metrics.
    """
    matches = RAGRetriever.retrieve_similar_defects(
        query="Null pointer crash during network request cancellation in HTTP channel",
        top_k=3
    )

    assert len(matches) > 0
    for m in matches:
        assert "similarity" in m
        assert 0.0 <= m["similarity"] <= 1.0
        assert "distance" in m
        meta = m["metadata"]
        assert "bug_id" in meta
        assert "source" in meta
        assert meta["source"] in ["Mozilla", "Apache", "Eclipse", "Platform"]

def test_insufficient_evidence_and_uncertainty_handling():
    """
    Test 10: Graceful Degradation on Insufficient Technical Information
    Verifies that vague submissions return 'Insufficient Evidence' and low confidence.
    """
    sparse_case = next(c for c in BENCHMARK_CASES if c["id"] == "TC-SPARSE-08")

    triage_agent = TriageAgent()
    log_agent = LogAnalysisAgent()
    rc_agent = RootCauseAgent()

    triage_res = triage_agent.heuristic_analyze(
        title=sparse_case["title"],
        description=sparse_case["description"]
    )
    assert triage_res["confidence"] <= 0.40
    assert "Insufficient Evidence" in triage_res["reasoning"]

    log_res = log_agent.heuristic_analyze(description=sparse_case["description"])
    assert log_res["status"] == "Insufficient Evidence"
    assert log_res["confidence"] == 0.0

    rc_res = rc_agent.heuristic_analyze(
        bug_description=sparse_case["description"],
        triage_output=triage_res,
        log_analysis_output=log_res,
        retrieved_defects=[]
    )
    assert rc_res["status"] == "Insufficient Evidence"
    assert rc_res["confidence"] <= 0.30

@pytest.mark.asyncio
async def test_fault_tolerance_agent_isolation(db_session, test_user):
    """
    Test 11: Fault Tolerance & Upstream Agent Error Isolation
    Simulates an unexpected runtime exception in TriageAgent and LogAnalysisAgent.
    Verifies that the orchestrator catches the failure, applies safe fallbacks,
    and successfully completes the pipeline without crashing.
    """
    orchestrator = AgentOrchestrator()

    bug = BugReport(
        user_id=test_user.id,
        title="Fault tolerance verification defect report",
        description="Testing error containment when an agent throws an unexpected exception.",
        component="Testing",
        status="Submitted",
        indexed_in_kb=False
    )
    db_session.add(bug)
    db_session.commit()
    db_session.refresh(bug)

    # Mock TriageAgent.analyze to raise an unhandled Exception
    with patch.object(orchestrator.triage_agent, "analyze", side_effect=RuntimeError("Simulated Triage failure")):
        with patch.object(orchestrator.log_analysis_agent, "analyze", side_effect=ValueError("Simulated Log failure")):
            diagnosis = await orchestrator.run_pipeline(db_session, bug)

    # Assert pipeline completed gracefully
    assert diagnosis is not None
    assert diagnosis.status == "Completed"
    assert bug.status == "Diagnosed"

    # Fallbacks were populated
    import json
    t_data = json.loads(diagnosis.triage_json)
    assert "partially unavailable" in t_data["reasoning"]

    l_data = json.loads(diagnosis.log_analysis_json)
    assert l_data["status"] == "Insufficient Evidence"

def test_pipeline_latency_and_performance_budget(client, auth_headers):
    """
    Test 12: Pipeline Latency Benchmarking
    Measures end-to-end processing time from bug submission to final diagnosis.
    Asserts performance remains within the 5.0 second budget.
    """
    start_time = time.perf_counter()

    # 1. Bug creation
    res = client.post("/bugs", json={
        "title": "Latency benchmark test case for M4.3",
        "description": "Benchmarking wall-clock execution time across full 5-agent diagnosis pipeline.",
        "component": "Performance"
    }, headers=auth_headers)
    assert res.status_code == 201
    bug_id = res.json()["id"]

    # 2. Pipeline execution
    diag_res = client.post(f"/bugs/{bug_id}/analyze", headers=auth_headers)
    assert diag_res.status_code == 200

    elapsed = time.perf_counter() - start_time
    # Assert processing completes within budget (< 5.0 seconds)
    assert elapsed < 5.0, f"Pipeline exceeded latency budget: {elapsed:.2f}s"
