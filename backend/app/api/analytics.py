from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.api.auth import get_current_user_optional
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    ComponentHotspot,
    ExceptionPattern,
    RootCauseTheme,
    SemanticCluster,
    TimeTrendAnalysis,
    AnalyticsFilterOptions
)

router = APIRouter(prefix="/analytics", tags=["Defect Pattern Analytics"])

@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(
    component: Optional[str] = Query(None, description="Filter by component name"),
    severity: Optional[str] = Query(None, description="Filter by severity (Critical, High, Medium, Low)"),
    priority: Optional[str] = Query(None, description="Filter by priority (Critical, High, Medium, Low)"),
    exception_type: Optional[str] = Query(None, description="Filter by exception type"),
    source: Optional[str] = Query("all", description="Source: 'all', 'submitted', or 'historical'"),
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Returns full comprehensive defect pattern analytics overview including:
    - High-level KPIs and recurrence rates
    - Severity and Priority distributions
    - Component hotspots and vulnerability ranking
    - Top recurring exception types and failure points
    - Root cause themes with actionable remediation mappings
    - Semantic bug clusters using vector similarity
    - Time-series defect trends and velocity
    """
    return AnalyticsService.get_overview(
        db=db,
        component=component,
        severity=severity,
        priority=priority,
        exception_type=exception_type,
        source=source,
        date_from=date_from,
        date_to=date_to
    )

@router.get("/components", response_model=List[ComponentHotspot])
def get_component_hotspots(
    source: Optional[str] = Query("all"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Returns recurring component hotspots and failure density rankings."""
    overview = AnalyticsService.get_overview(db=db, source=source)
    return overview.component_hotspots

@router.get("/exceptions", response_model=List[ExceptionPattern])
def get_exception_patterns(
    component: Optional[str] = Query(None),
    source: Optional[str] = Query("all"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Returns recurring exception signatures and failure points."""
    overview = AnalyticsService.get_overview(db=db, component=component, source=source)
    return overview.top_exception_patterns

@router.get("/root-causes", response_model=List[RootCauseTheme])
def get_root_cause_themes(
    component: Optional[str] = Query(None),
    source: Optional[str] = Query("all"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Returns recurring root causes mapped to actionable remediation patterns."""
    overview = AnalyticsService.get_overview(db=db, component=component, source=source)
    return overview.root_cause_themes

@router.get("/clusters", response_model=List[SemanticCluster])
def get_semantic_clusters(
    component: Optional[str] = Query(None),
    source: Optional[str] = Query("all"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Returns semantically clustered defect groups using vector similarity."""
    overview = AnalyticsService.get_overview(db=db, component=component, source=source)
    return overview.semantic_clusters

@router.get("/trends", response_model=TimeTrendAnalysis)
def get_time_trends(
    component: Optional[str] = Query(None),
    source: Optional[str] = Query("all"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Returns time-based defect frequency trends and velocity."""
    overview = AnalyticsService.get_overview(db=db, component=component, source=source)
    return overview.time_trends

@router.get("/filters", response_model=AnalyticsFilterOptions)
def get_analytics_filters(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Returns available filter options for interactive UI filtering."""
    return AnalyticsService.get_filter_options(db=db)
