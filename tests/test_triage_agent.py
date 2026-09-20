import pytest
from app.agents.triage_agent import TriageAgent

@pytest.mark.asyncio
async def test_triage_critical_crash():
    agent = TriageAgent()
    res = await agent.analyze(
        title="Application crash with fatal segfault in rendering worker",
        description="Every time 3D canvas loads, process dies with fatal segfault in WebGL driver.",
        stack_trace="Segmentation fault (core dumped) at 0x7fff4010"
    )
    assert res["severity"] == "Critical"
    assert res["priority"] == "Critical"
    assert res["confidence"] >= 0.85
    assert "crash" in res["reasoning"].lower() or "fatal" in res["reasoning"].lower()

@pytest.mark.asyncio
async def test_triage_high_npe_auth():
    agent = TriageAgent()
    res = await agent.analyze(
        title="Login fails with NullPointerException",
        description="Users cannot login when username has trailing whitespace.",
        stack_trace="java.lang.NullPointerException at AuthService.login(AuthService.java:42)"
    )
    assert res["severity"] == "High"
    assert "Authentication" in res["affected_component"]
    assert res["confidence"] >= 0.80

@pytest.mark.asyncio
async def test_triage_insufficient_evidence():
    agent = TriageAgent()
    res = await agent.analyze(
        title="bug",
        description="it broke"
    )
    assert res["confidence"] <= 0.50
    assert "Insufficient Evidence" in res["reasoning"]
