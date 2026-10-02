import pytest
from app.models.bug_report import BugReport
from app.models.historical_defect import HistoricalDefect
from app.rag.vector_store import VectorStore

def test_kb_growth_stats_endpoint(client):
    """Verify that GET /api/knowledge-base/growth/stats returns valid growth metrics."""
    response = client.get("/api/knowledge-base/growth/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_knowledge_base_records" in data
    assert "platform_contributed_records" in data
    assert "total_vector_chunks" in data
    assert "growth_percentage" in data
    assert isinstance(data["recent_platform_promotions"], list)

def test_kb_growth_candidates_endpoint(client):
    """Verify that GET /api/knowledge-base/growth/candidates returns candidate defects."""
    response = client.get("/api/knowledge-base/growth/candidates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        c = data[0]
        assert "bug_id" in c
        assert "title" in c
        assert "is_eligible_for_kb" in c
        assert "indexed_in_kb" in c

def test_quality_gate_rejection_for_incomplete_bug(client, db_session, test_user):
    """Verify that an incomplete bug report fails the Quality Gate."""
    incomplete_bug = BugReport(
        user_id=test_user.id,
        title="Crash",
        description="Short",
        component=None,
        stack_trace=None,
        error_logs=None,
        status="Open",
        indexed_in_kb=False
    )
    db_session.add(incomplete_bug)
    db_session.commit()
    db_session.refresh(incomplete_bug)

    response = client.get(f"/api/knowledge-base/growth/validate/{incomplete_bug.id}")
    assert response.status_code == 200
    gate = response.json()
    assert gate["is_eligible"] is False
    assert len(gate["blocking_reasons"]) > 0

    promote_res = client.post(f"/api/knowledge-base/growth/promote/{incomplete_bug.id}", json={
        "resolution_notes": "Attempting early promotion without required logs."
    })
    assert promote_res.status_code == 400
    assert "Quality Gate validation" in promote_res.json()["detail"]

def test_resolution_and_promotion_workflow(client, db_session, test_user):
    """
    Test the complete M4.2 workflow:
    1. Create bug with logs and stack trace
    2. Submit resolution and confirmed fix
    3. Validate quality gate passes
    4. Promote to Knowledge Base (384-d vectors, ChromaDB, HistoricalDefect)
    5. Verify duplicate prevention
    6. Verify downstream retrievability
    """
    valid_bug = BugReport(
        user_id=test_user.id,
        title="Deadlock in database connection pool during concurrent transaction rollback",
        description="Under high concurrent write workload, connection checkout hangs indefinitely when a transaction aborts.",
        component="DatabaseConnectionPool",
        stack_trace="java.lang.IllegalStateException: Connection pool exhausted at ConnectionManager.acquire(ConnectionManager.java:142)\n at PoolWorker.run(PoolWorker.java:88)",
        error_logs="[ERROR] Connection timeout after 30000ms. Active leases: 50/50. Thread deadlock detected on pool lock.",
        status="Under Review",
        indexed_in_kb=False
    )
    db_session.add(valid_bug)
    db_session.commit()
    db_session.refresh(valid_bug)

    resolve_payload = {
        "resolution_notes": "Implemented synchronized release lock and timeout failover in ConnectionManager.acquire to release stranded lease on transaction rollback abort.",
        "confirmed_fix_code": "try {\n    lock.tryAcquire(5000, TimeUnit.MILLISECONDS);\n} finally {\n    connection.close();\n}",
        "confirmed_root_cause": "Unreleased mutex on transaction abort caused connection exhaustion",
        "component": "DatabaseConnectionPool"
    }

    resolve_res = client.post(f"/api/knowledge-base/growth/resolve/{valid_bug.id}", json=resolve_payload)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["bug_status"] == "Resolved"

    gate_res = client.get(f"/api/knowledge-base/growth/validate/{valid_bug.id}")
    assert gate_res.status_code == 200
    gate_data = gate_res.json()
    assert gate_data["is_eligible"] is True
    assert gate_data["quality_score"] >= 0.65
    assert len(gate_data["blocking_reasons"]) == 0

    initial_chunks = VectorStore.count()

    promote_res = client.post(f"/api/knowledge-base/growth/promote/{valid_bug.id}")
    assert promote_res.status_code == 200
    promo_data = promote_res.json()
    assert promo_data["success"] is True
    assert promo_data["dataset_source"] == "Platform"
    assert promo_data["assigned_kb_id"].startswith("PLATFORM-")
    assert promo_data["indexed_chunks_count"] > 0

    assert VectorStore.count() >= initial_chunks + promo_data["indexed_chunks_count"]

    hist_rec = db_session.query(HistoricalDefect).filter(HistoricalDefect.bug_id == promo_data["assigned_kb_id"]).first()
    assert hist_rec is not None
    assert hist_rec.dataset_source == "Platform"
    assert hist_rec.component == "DatabaseConnectionPool"
    assert "synchronized release lock" in hist_rec.resolution

    db_session.refresh(valid_bug)
    assert valid_bug.indexed_in_kb is True
    assert valid_bug.status == "Resolved"

    dup_res = client.post(f"/api/knowledge-base/growth/promote/{valid_bug.id}")
    assert dup_res.status_code == 400
    assert "already indexed" in dup_res.json()["detail"].lower()

    list_res = client.get("/api/knowledge-base/defects?source=Platform")
    assert list_res.status_code == 200
    platform_defects = list_res.json()
    assert any(d["bug_id"] == promo_data["assigned_kb_id"] for d in platform_defects)

    search_res = client.post("/api/knowledge-base/search", json={
        "query": "database connection pool deadlock during rollback acquire",
        "top_k": 5
    })
    assert search_res.status_code == 200
    search_results = search_res.json()["results"]
    assert len(search_results) > 0
    found = any(r["bug_id"] == promo_data["assigned_kb_id"] for r in search_results)
    assert found is True

