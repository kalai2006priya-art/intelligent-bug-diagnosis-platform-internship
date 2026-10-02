from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ==========================================
# 1. Distribution & KPI Schemas
# ==========================================
class DistributionItem(BaseModel):
    category: str
    count: int
    percentage: float

class AnalyticsKPIs(BaseModel):
    total_defects_analyzed: int
    recurring_pattern_rate: float = Field(..., description="Percentage of bugs belonging to a recurring pattern or cluster")
    top_affected_component: str
    critical_high_percentage: float
    duplicate_defect_count: int
    unique_exception_types: int

# ==========================================
# 2. Component Hotspots
# ==========================================
class ComponentHotspot(BaseModel):
    component: str
    defect_count: int
    percentage_of_total: float
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    recurrence_rate: float
    top_exceptions: List[str] = Field(default_factory=list)
    risk_level: str = Field(..., description="High, Medium, or Low based on failure density and severity")

# ==========================================
# 3. Exception & Failure Patterns
# ==========================================
class ExceptionPattern(BaseModel):
    exception_type: str
    occurrence_count: int
    percentage: float
    affected_components: List[str] = Field(default_factory=list)
    sample_failure_points: List[str] = Field(default_factory=list)
    sample_error_messages: List[str] = Field(default_factory=list)
    severity_breakdown: Dict[str, int] = Field(default_factory=dict)

# ==========================================
# 4. Root Cause & Remediation Themes
# ==========================================
class RemediationPatternItem(BaseModel):
    pattern_title: str
    recommended_action: str
    frequency: int
    example_code_snippet: Optional[str] = None

class RootCauseTheme(BaseModel):
    theme_id: str
    theme_name: str
    description: str
    frequency: int
    percentage: float
    associated_components: List[str] = Field(default_factory=list)
    common_remediations: List[RemediationPatternItem] = Field(default_factory=list)
    sample_bug_titles: List[str] = Field(default_factory=list)

# ==========================================
# 5. Semantic Bug Clusters
# ==========================================
class ClusterMemberDefect(BaseModel):
    id: str
    bug_id: str
    title: str
    severity: str
    component: str
    similarity_to_centroid: float
    created_at: Optional[str] = None

class SemanticCluster(BaseModel):
    cluster_id: str
    cluster_theme: str
    defect_count: int
    percentage_of_total: float
    average_similarity: float
    representative_defect: str
    primary_component: str
    dominant_severity: str
    members: List[ClusterMemberDefect] = Field(default_factory=list)

# ==========================================
# 6. Time-Based Trends
# ==========================================
class TimeTrendPoint(BaseModel):
    period: str
    total_count: int
    critical_count: int
    high_count: int
    top_component: Optional[str] = None

class TimeTrendAnalysis(BaseModel):
    interval: str = "daily"
    trend_direction: str = Field(..., description="'Increasing', 'Decreasing', or 'Stable'")
    velocity_percentage: float = Field(..., description="Change percentage compared to previous period")
    timeline: List[TimeTrendPoint] = Field(default_factory=list)

# ==========================================
# 7. Complete Overview Response
# ==========================================
class AnalyticsOverviewResponse(BaseModel):
    kpis: AnalyticsKPIs
    severity_distribution: List[DistributionItem]
    priority_distribution: List[DistributionItem]
    duplicate_distribution: List[DistributionItem]
    component_hotspots: List[ComponentHotspot]
    top_exception_patterns: List[ExceptionPattern]
    root_cause_themes: List[RootCauseTheme]
    semantic_clusters: List[SemanticCluster]
    time_trends: TimeTrendAnalysis
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# ==========================================
# 8. Filter Query Parameters & Options
# ==========================================
class AnalyticsFilterOptions(BaseModel):
    available_components: List[str]
    available_severities: List[str]
    available_priorities: List[str]
    available_exception_types: List[str]
    available_sources: List[str]
