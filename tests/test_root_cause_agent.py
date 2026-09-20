import pytest
from app.agents.root_cause_agent import RootCauseAgent

@pytest.mark.asyncio
async def test_root_cause_with_historical_evidence():
    agent = RootCauseAgent()
    triage_out = {"severity": "High", "affected_component": "Authentication & Authorization"}
    log_out = {
        "status": "Success",
        "exception_type": "NullPointerException",
        "failure_point": "AuthService.java:42",
        "affected_code_path": "AuthController -> AuthService.login"
    }
    retrieved = [
        {
            "chunk_id": "c1",
            "similarity": 0.89,
            "text": "NPE in AuthService when token is null",
            "metadata": {"bug_id": "SPARK-14920", "source": "Apache", "title": "NPE in BroadcastExchange", "resolution": "FIXED"}
        }
    ]

    res = await agent.analyze(
        bug_description="User gets NullPointerException when logging in with empty credentials",
        triage_output=triage_out,
        log_analysis_output=log_out,
        retrieved_defects=retrieved
    )

    assert res["status"] == "Supported"
    assert "null" in res["root_cause_hypothesis"].lower()
    assert len(res["supporting_evidence"]) >= 1
    assert res["supporting_evidence"][0]["bug_id"] == "SPARK-14920"
    assert "AuthService.java:42" in res["reasoning"]

@pytest.mark.asyncio
async def test_root_cause_insufficient_evidence():
    agent = RootCauseAgent()
    res = await agent.analyze(
        bug_description="broken",
        triage_output={"severity": "Low", "affected_component": "General"},
        log_analysis_output={"status": "Insufficient Evidence", "exception_type": None, "failure_point": None},
        retrieved_defects=[]
    )
    assert res["status"] == "Insufficient Evidence"
    assert "insufficient" in res["root_cause_hypothesis"].lower()
