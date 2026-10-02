import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.services.analytics_service import AnalyticsService

client = TestClient(app)

def test_analytics_overview_endpoint():
    """Verify that GET /api/analytics/overview returns a 200 OK with full schema structure."""
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()

    # 1. KPIs
    assert "kpis" in data
    kpis = data["kpis"]
    assert kpis["total_defects_analyzed"] >= 0
    assert "recurring_pattern_rate" in kpis
    assert "top_affected_component" in kpis
    assert "critical_high_percentage" in kpis

    # 2. Distributions
    assert "severity_distribution" in data
    assert "priority_distribution" in data
    assert "duplicate_distribution" in data

    # 3. Hotspots & Patterns
    assert "component_hotspots" in data
    assert "top_exception_patterns" in data
    assert "root_cause_themes" in data
    assert "semantic_clusters" in data
    assert "time_trends" in data

def test_component_hotspots_endpoint():
    """Verify component hotspots ranking and risk level classification."""
    response = client.get("/api/analytics/components")
    assert response.status_code == 200
    hotspots = response.json()
    assert isinstance(hotspots, list)
    if len(hotspots) > 0:
        first = hotspots[0]
        assert "component" in first
        assert "defect_count" in first
        assert "risk_level" in first
        assert first["risk_level"] in ["High", "Medium", "Low"]

def test_exception_patterns_endpoint():
    """Verify extraction of recurring exception types and failure signatures."""
    response = client.get("/api/analytics/exceptions")
    assert response.status_code == 200
    exceptions = response.json()
    assert isinstance(exceptions, list)
    for exc in exceptions:
        assert "exception_type" in exc
        assert "occurrence_count" in exc
        assert "percentage" in exc

def test_root_cause_themes_endpoint():
    """Verify recurring root cause themes and remediation pattern mappings."""
    response = client.get("/api/analytics/root-causes")
    assert response.status_code == 200
    themes = response.json()
    assert isinstance(themes, list)
    for theme in themes:
        assert "theme_id" in theme
        assert "theme_name" in theme
        assert "frequency" in theme
        assert "common_remediations" in theme
        if len(theme["common_remediations"]) > 0:
            rem = theme["common_remediations"][0]
            assert "pattern_title" in rem
            assert "recommended_action" in rem

def test_semantic_clusters_endpoint():
    """Verify semantic defect clustering using vector similarity."""
    response = client.get("/api/analytics/clusters")
    assert response.status_code == 200
    clusters = response.json()
    assert isinstance(clusters, list)
    for cluster in clusters:
        assert "cluster_id" in cluster
        assert "cluster_theme" in cluster
        assert "defect_count" in cluster
        assert "average_similarity" in cluster
        assert cluster["average_similarity"] >= 0.5
        assert "members" in cluster

def test_time_trends_endpoint():
    """Verify time-series defect trend analysis."""
    response = client.get("/api/analytics/trends")
    assert response.status_code == 200
    trends = response.json()
    assert "trend_direction" in trends
    assert trends["trend_direction"] in ["Increasing", "Decreasing", "Stable"]
    assert "timeline" in trends

def test_analytics_filters_endpoint():
    """Verify available filter options."""
    response = client.get("/api/analytics/filters")
    assert response.status_code == 200
    filters = response.json()
    assert "available_components" in filters
    assert "available_severities" in filters
    assert "available_sources" in filters

def test_analytics_service_filtering():
    """Directly test service filtering logic with database session."""
    db = SessionLocal()
    try:
        # Overview without filters
        all_overview = AnalyticsService.get_overview(db, source="all")
        total_all = all_overview.kpis.total_defects_analyzed

        # Filter by severity
        crit_overview = AnalyticsService.get_overview(db, severity="Critical")
        assert crit_overview.kpis.total_defects_analyzed <= total_all

        # Filter by source
        hist_overview = AnalyticsService.get_overview(db, source="historical")
        assert hist_overview.kpis.total_defects_analyzed <= total_all
    finally:
        db.close()
