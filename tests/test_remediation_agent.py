import pytest
from app.agents.remediation_agent import RemediationAgent

@pytest.mark.asyncio
async def test_remediation_npe_recommendations():
    agent = RemediationAgent()
    triage = {"severity": "High", "affected_component": "Authentication"}
    log_analysis = {
        "status": "Success",
        "exception_type": "NullPointerException",
        "failure_point": "AuthService.java:38"
    }
    root_cause = {
        "status": "Supported",
        "root_cause_hypothesis": "Unvalidated null payload passed into token serializer.",
        "supporting_evidence": [{"bug_id": "SPARK-14920"}]
    }
    duplicate = {
        "status": "Related Issue",
        "matches": [{"bug_id": "SPARK-14920"}]
    }

    res = await agent.analyze(triage, log_analysis, root_cause, duplicate)
    assert res["status"] == "Supported"
    assert len(res["recommendations"]) >= 1
    rec1 = res["recommendations"][0]
    assert "null" in rec1["recommendation"].lower()
    assert rec1["basis"] in ["Historical Evidence", "General Best Practice", "Agent Recommendation"]
    assert len(rec1["validation_steps"]) >= 1
    assert "AuthService.java:38" in rec1["affected_module"]

@pytest.mark.asyncio
async def test_remediation_insufficient_evidence():
    agent = RemediationAgent()
    triage = {"severity": "Low", "affected_component": "General"}
    log_analysis = {"status": "Insufficient Evidence"}
    root_cause = {"status": "Insufficient Evidence"}
    duplicate = {"status": "Insufficient Evidence", "matches": []}

    res = await agent.analyze(triage, log_analysis, root_cause, duplicate)
    assert res["status"] == "Insufficient Evidence"
    assert len(res["recommendations"]) == 0
