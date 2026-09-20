import pytest
from app.agents.duplicate_detection_agent import DuplicateDetectionAgent

@pytest.mark.asyncio
async def test_duplicate_likely_duplicate():
    agent = DuplicateDetectionAgent()
    retrieved = [
        {
            "chunk_id": "c1",
            "similarity": 0.91,
            "text": "Exact crash in HTTP channel listener",
            "metadata": {"bug_id": "MOZ-104820", "source": "Mozilla", "title": "Crash in OnStopRequest", "resolution": "FIXED"}
        }
    ]
    res = await agent.analyze(
        bug_title="Null pointer crash in nsHttpChannel::OnStopRequest",
        bug_description="Browser crashes when download is cancelled before stream finishes.",
        retrieved_defects=retrieved
    )
    assert res["status"] == "Likely Duplicate"
    assert len(res["matches"]) >= 1
    assert res["matches"][0]["bug_id"] == "MOZ-104820"
    assert res["matches"][0]["similarity"] == 0.91

@pytest.mark.asyncio
async def test_duplicate_related_issue():
    agent = DuplicateDetectionAgent()
    retrieved = [
        {
            "chunk_id": "c2",
            "similarity": 0.72,
            "text": "Similar timeout in connection manager",
            "metadata": {"bug_id": "HTTP-101", "source": "Apache", "title": "Connection timeout", "resolution": "FIXED"}
        }
    ]
    res = await agent.analyze(
        bug_title="Slow API response and occasional connection drop",
        bug_description="Clients report periodic network drops during heavy batch requests.",
        retrieved_defects=retrieved
    )
    assert res["status"] == "Related Issue"

@pytest.mark.asyncio
async def test_duplicate_new_unmatched():
    agent = DuplicateDetectionAgent()
    retrieved = [
        {
            "chunk_id": "c3",
            "similarity": 0.45,
            "text": "Unrelated UI defect",
            "metadata": {"bug_id": "ECL-200", "source": "Eclipse", "title": "Button alignment", "resolution": "CLOSED"}
        }
    ]
    res = await agent.analyze(
        bug_title="Novel quantum cryptography accelerator failed bit check",
        bug_description="Hardware driver returned malformed parity bits during handshake sequence.",
        retrieved_defects=retrieved
    )
    assert res["status"] == "New / Unmatched"

@pytest.mark.asyncio
async def test_duplicate_insufficient_evidence():
    agent = DuplicateDetectionAgent()
    res = await agent.analyze(
        bug_title="err",
        bug_description="x",
        retrieved_defects=[]
    )
    assert res["status"] == "Insufficient Evidence"
