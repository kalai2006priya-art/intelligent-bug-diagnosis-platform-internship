import pytest

def test_full_agent_orchestration_pipeline(client, auth_headers):
    # 1. Create a bug
    create_resp = client.post("/bugs", json={
        "title": "Null pointer crash in HTTP network request callback when cancelled",
        "description": "Firefox crashes when a large download is cancelled before stream completes. nsHttpChannel fails to check if mListener is null before calling OnStopRequest.",
        "stack_trace": "Crash [@ nsHttpChannel::OnStopRequest(nsIRequest*, nsISupports*, tag_nsresult)]\n0 xul.dll!nsHttpChannel::OnStopRequest [nsHttpChannel.cpp:6840]",
        "component": "Networking",
        "environment": "Windows 11 x64"
    }, headers=auth_headers)
    assert create_resp.status_code == 201
    bug_id = create_resp.json()["id"]

    # 2. Trigger 5-agent analysis orchestration
    analyze_resp = client.post(f"/bugs/{bug_id}/analyze", headers=auth_headers)
    assert analyze_resp.status_code == 200
    diag = analyze_resp.json()

    # 3. Verify all 5 agents executed and populated findings
    assert diag["status"] == "Completed"
    assert diag["overall_confidence"] > 0.0

    # Triage Agent
    assert "severity" in diag["triage"]
    assert diag["triage"]["severity"] in ["Critical", "High", "Medium", "Low"]
    assert "priority" in diag["triage"]
    assert "affected_component" in diag["triage"]

    # Log Analysis Agent
    assert "exception_type" in diag["log_analysis"]
    assert diag["log_analysis"]["failure_point"] is not None

    # Root Cause Agent
    assert "root_cause_hypothesis" in diag["root_cause"]
    assert diag["root_cause"]["status"] == "Supported"
    assert isinstance(diag["root_cause"]["supporting_evidence"], list)

    # Duplicate Detection Agent
    assert "status" in diag["duplicate_detection"]
    assert isinstance(diag["duplicate_detection"]["matches"], list)

    # Remediation Agent
    assert "recommendations" in diag["remediation"]
    assert len(diag["remediation"]["recommendations"]) >= 1
    assert "validation_steps" in diag["remediation"]["recommendations"][0]

    # 4. Fetch stored diagnosis via GET endpoint
    get_diag_resp = client.get(f"/bugs/{bug_id}/diagnosis", headers=auth_headers)
    assert get_diag_resp.status_code == 200
    assert get_diag_resp.json()["id"] == diag["id"]

    # 5. Check bug report status updated to Diagnosed
    bug_resp = client.get(f"/bugs/{bug_id}", headers=auth_headers)
    assert bug_resp.json()["status"] == "Diagnosed"
    assert bug_resp.json()["has_diagnosis"] is True
