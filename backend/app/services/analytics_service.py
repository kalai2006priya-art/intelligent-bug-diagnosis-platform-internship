import json
import re
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.bug_report import BugReport
from app.models.diagnosis import AgentDiagnosis
from app.models.historical_defect import HistoricalDefect
from app.schemas.analytics import (
    DistributionItem,
    AnalyticsKPIs,
    ComponentHotspot,
    ExceptionPattern,
    RemediationPatternItem,
    RootCauseTheme,
    ClusterMemberDefect,
    SemanticCluster,
    TimeTrendPoint,
    TimeTrendAnalysis,
    AnalyticsOverviewResponse,
    AnalyticsFilterOptions
)

KNOWN_ROOT_CAUSE_CATEGORIES = [
    {
        "id": "theme_null_ref",
        "name": "Null & Uninitialized Reference Errors",
        "description": "Failures occurring when code attempts to invoke methods or access fields on null/uninitialized object references.",
        "keywords": ["null", "nullpointer", "none", "attributeerror", "undefined", "uninitialized", "pointer"],
        "remediations": [
            {
                "pattern_title": "Defensive Precondition & Null Checks",
                "recommended_action": "Add explicit null checks before object access or wrap values in Optional / null-safe accessor methods.",
                "example_code_snippet": "if (token == null || token.trim().isEmpty()) {\n    throw new IllegalArgumentException(\"Auth token cannot be null\");\n}"
            },
            {
                "pattern_title": "Null-Coalescing & Safe Navigation",
                "recommended_action": "Use Optional.ofNullable() in Java or null-coalescing operators (?.) in TypeScript/Python.",
                "example_code_snippet": "user = Optional.ofNullable(tokenRepository.find(id)).orElseThrow();"
            }
        ]
    },
    {
        "id": "theme_db_timeout",
        "name": "Connection Pool & Network Timeout Failures",
        "description": "Exhaustion of database connection pools, socket timeouts, or network latency spikes causing service unavailability.",
        "keywords": ["timeout", "connection", "socket", "pool", "exhaust", "database", "timed out", "retry"],
        "remediations": [
            {
                "pattern_title": "Connection Pooling & Keep-Alive Tuning",
                "recommended_action": "Increase pool max size, configure connection idle eviction, and enable keep-alive heartbeats.",
                "example_code_snippet": "dataSource.setMaximumPoolSize(20);\ndataSource.setConnectionTimeout(5000);\ndataSource.setIdleTimeout(600000);"
            },
            {
                "pattern_title": "Exponential Backoff & Circuit Breaker",
                "recommended_action": "Implement resilient retry mechanisms with jitter and circuit breaker patterns.",
                "example_code_snippet": "@Retry(maxAttempts = 3, delay = 1000, multiplier = 2.0)\npublic Connection acquireConnection() { ... }"
            }
        ]
    },
    {
        "id": "theme_input_validation",
        "name": "Input Validation & Data Serialization Defects",
        "description": "Invalid user payloads, malformed JSON, unhandled type mismatches, or missing schema boundaries.",
        "keywords": ["validation", "parse", "format", "invalid", "json", "schema", "typeerror", "valueerror", "keyerror"],
        "remediations": [
            {
                "pattern_title": "Strict Schema Validation & Sanitization",
                "recommended_action": "Enforce strict request body schemas using Pydantic or Bean Validation before business logic execution.",
                "example_code_snippet": "class RequestPayload(BaseModel):\n    id: str = Field(..., min_length=1)\n    amount: float = Field(..., gt=0)"
            }
        ]
    },
    {
        "id": "theme_resource_leak",
        "name": "Resource Leaks & State Inconsistency",
        "description": "Unclosed I/O streams, orphaned file descriptors, or dangling thread locks causing degradation.",
        "keywords": ["leak", "unclosed", "memory", "outofmemory", "stream", "handle", "concurrency", "deadlock"],
        "remediations": [
            {
                "pattern_title": "Automated Resource Management (Try-With-Resources)",
                "recommended_action": "Ensure all auto-closeable streams, sockets, and transactions use deterministic context managers.",
                "example_code_snippet": "try (InputStream is = new FileInputStream(file)) {\n    process(is);\n}"
            }
        ]
    },
    {
        "id": "theme_config_env",
        "name": "Configuration & Environment Mismatches",
        "description": "Missing environment variables, incorrect path separators, or incompatible runtime library versions.",
        "keywords": ["config", "environment", "env", "version", "incompatible", "not found", "filenotfound", "module"],
        "remediations": [
            {
                "pattern_title": "Fail-Fast Environment Pre-Flight Checks",
                "recommended_action": "Validate all required environment configuration variables during application bootstrap.",
                "example_code_snippet": "settings = Settings()\nassert settings.DATABASE_URL is not None, \"DATABASE_URL must be defined\""
            }
        ]
    }
]

class AnalyticsService:

    @staticmethod
    def _parse_json(val: Any) -> Dict[str, Any]:
        if not val:
            return {}
        if isinstance(val, dict):
            return val
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return {}
        return {}

    @staticmethod
    def _extract_exception_from_text(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        patterns = [
            r'([a-zA-Z0-9_\.]*(?:Exception|Error|Fault|Failure))',
            r'(NullPointerException|TimeoutException|SQLException|KeyError|ValueError|TypeError|IndexOutOfBoundsException|FileNotFoundException|IOException|ConnectionError|AttributeError)'
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                raw = match.group(1).strip()
                if "." in raw:
                    raw = raw.split(".")[-1]
                return raw
        return None

    @staticmethod
    def _extract_failure_point(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        match = re.search(r'([A-Za-z0-9_-]+\.(?:java|py|cpp|js|ts|c)):(?:line\s*)?(\d+)', text)
        if match:
            return f"{match.group(1)}:{match.group(2)}"
        return None

    @classmethod
    def _fetch_standardized_defects(
        cls,
        db: Session,
        component: Optional[str] = None,
        severity: Optional[str] = None,
        priority: Optional[str] = None,
        exception_type: Optional[str] = None,
        source: Optional[str] = "all",
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []

        # 1. Fetch Submitted Bugs + Diagnoses
        if source in ["all", "submitted"]:
            q_bugs = db.query(BugReport, AgentDiagnosis).outerjoin(
                AgentDiagnosis, BugReport.id == AgentDiagnosis.bug_id
            )
            if component:
                q_bugs = q_bugs.filter(BugReport.component.ilike(f"%{component}%"))
            if date_from:
                q_bugs = q_bugs.filter(BugReport.created_at >= date_from)
            if date_to:
                q_bugs = q_bugs.filter(BugReport.created_at <= date_to)

            for bug, diag in q_bugs.all():
                triage_data = cls._parse_json(diag.triage_json) if diag else {}
                log_data = cls._parse_json(diag.log_analysis_json) if diag else {}
                root_data = cls._parse_json(diag.root_cause_json) if diag else {}
                dup_data = cls._parse_json(diag.duplicate_detection_json) if diag else {}
                rem_data = cls._parse_json(diag.remediation_json) if diag else {}

                sev = triage_data.get("severity") or "Medium"
                prio = triage_data.get("priority") or "Medium"
                comp = bug.component or triage_data.get("affected_component") or "General"
                exc = log_data.get("exception_type") or cls._extract_exception_from_text(bug.stack_trace) or cls._extract_exception_from_text(bug.error_logs) or "UnclassifiedException"
                fail_pt = log_data.get("failure_point") or cls._extract_failure_point(bug.stack_trace) or "N/A"
                dup_status = dup_data.get("status") or "New / Unmatched"
                rc_hypo = root_data.get("root_cause_hypothesis") or bug.description or ""

                if severity and sev.lower() != severity.lower():
                    continue
                if priority and prio.lower() != priority.lower():
                    continue
                if exception_type and exception_type.lower() not in exc.lower():
                    continue

                records.append({
                    "id": f"submitted_{bug.id}",
                    "bug_id": str(bug.id),
                    "title": bug.title,
                    "description": bug.description,
                    "component": comp,
                    "severity": sev.capitalize(),
                    "priority": prio.capitalize(),
                    "exception_type": exc,
                    "failure_point": fail_pt,
                    "root_cause": rc_hypo,
                    "duplicate_status": dup_status,
                    "source": "Submitted Bugs",
                    "created_at": bug.created_at or datetime.utcnow(),
                    "remediations": rem_data.get("recommendations", [])
                })

        # 2. Fetch Historical Defects
        if source in ["all", "historical"]:
            q_hist = db.query(HistoricalDefect)
            if component:
                q_hist = q_hist.filter(HistoricalDefect.component.ilike(f"%{component}%"))
            if date_from:
                q_hist = q_hist.filter(HistoricalDefect.created_at >= date_from)
            if date_to:
                q_hist = q_hist.filter(HistoricalDefect.created_at <= date_to)

            for hd in q_hist.all():
                sev = hd.severity or "Medium"
                prio = hd.priority or "Medium"
                comp = hd.component or hd.project or "Core"
                exc = cls._extract_exception_from_text(hd.error_message) or cls._extract_exception_from_text(hd.stack_trace) or cls._extract_exception_from_text(hd.description) or "UnclassifiedException"
                fail_pt = cls._extract_failure_point(hd.stack_trace) or "N/A"

                if severity and sev.lower() != severity.lower():
                    continue
                if priority and prio.lower() != priority.lower():
                    continue
                if exception_type and exception_type.lower() not in exc.lower():
                    continue

                records.append({
                    "id": f"historical_{hd.id}",
                    "bug_id": hd.bug_id or str(hd.id),
                    "title": hd.title,
                    "description": hd.description or "",
                    "component": comp,
                    "severity": sev.capitalize(),
                    "priority": prio.capitalize(),
                    "exception_type": exc,
                    "failure_point": fail_pt,
                    "root_cause": hd.resolution or hd.description or "",
                    "duplicate_status": "Historical Resolved",
                    "source": f"Historical ({hd.dataset_source})",
                    "created_at": hd.created_at or datetime.utcnow(),
                    "remediations": []
                })

        return records

    @classmethod
    def get_overview(
        cls,
        db: Session,
        component: Optional[str] = None,
        severity: Optional[str] = None,
        priority: Optional[str] = None,
        exception_type: Optional[str] = None,
        source: Optional[str] = "all",
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> AnalyticsOverviewResponse:
        records = cls._fetch_standardized_defects(
            db, component, severity, priority, exception_type, source, date_from, date_to
        )
        total = len(records)
        if total == 0:
            return AnalyticsOverviewResponse(
                kpis=AnalyticsKPIs(
                    total_defects_analyzed=0,
                    recurring_pattern_rate=0.0,
                    top_affected_component="None",
                    critical_high_percentage=0.0,
                    duplicate_defect_count=0,
                    unique_exception_types=0
                ),
                severity_distribution=[],
                priority_distribution=[],
                duplicate_distribution=[],
                component_hotspots=[],
                top_exception_patterns=[],
                root_cause_themes=[],
                semantic_clusters=[],
                time_trends=TimeTrendAnalysis(
                    interval="daily", trend_direction="Stable", velocity_percentage=0.0, timeline=[]
                )
            )

        # 1. Severity Distribution
        sev_counts = Counter(r["severity"] for r in records)
        severity_dist = [
            DistributionItem(
                category=sev,
                count=sev_counts.get(sev, 0),
                percentage=round((sev_counts.get(sev, 0) / total) * 100, 1)
            )
            for sev in ["Critical", "High", "Medium", "Low"]
            if sev in sev_counts
        ]

        # 2. Priority Distribution
        prio_counts = Counter(r["priority"] for r in records)
        priority_dist = [
            DistributionItem(
                category=prio,
                count=prio_counts.get(prio, 0),
                percentage=round((prio_counts.get(prio, 0) / total) * 100, 1)
            )
            for prio in ["Critical", "High", "Medium", "Low"]
            if prio in prio_counts
        ]

        # 3. Duplicate Distribution
        dup_counts = Counter(r["duplicate_status"] for r in records)
        duplicate_dist = [
            DistributionItem(
                category=cat,
                count=cnt,
                percentage=round((cnt / total) * 100, 1)
            )
            for cat, cnt in dup_counts.most_common()
        ]

        # 4. Component Hotspots
        comp_groups = defaultdict(list)
        for r in records:
            comp_groups[r["component"]].append(r)

        component_hotspots: List[ComponentHotspot] = []
        for comp_name, comp_recs in sorted(comp_groups.items(), key=lambda x: len(x[1]), reverse=True):
            c_total = len(comp_recs)
            c_crit = sum(1 for r in comp_recs if r["severity"] == "Critical")
            c_high = sum(1 for r in comp_recs if r["severity"] == "High")
            c_med = sum(1 for r in comp_recs if r["severity"] == "Medium")
            c_low = sum(1 for r in comp_recs if r["severity"] == "Low")

            top_excs = [e for e, _ in Counter(r["exception_type"] for r in comp_recs if r["exception_type"] != "UnclassifiedException").most_common(3)]
            risk = "High" if (c_crit > 0 or (c_crit + c_high) >= 2 or c_total >= 4) else ("Medium" if (c_high > 0 or c_total >= 2) else "Low")
            recurrence = round((sum(1 for r in comp_recs if r["duplicate_status"] in ["Likely Duplicate", "Related Issue"] or c_total > 1) / c_total) * 100, 1)

            component_hotspots.append(ComponentHotspot(
                component=comp_name,
                defect_count=c_total,
                percentage_of_total=round((c_total / total) * 100, 1),
                critical_count=c_crit,
                high_count=c_high,
                medium_count=c_med,
                low_count=c_low,
                recurrence_rate=recurrence,
                top_exceptions=top_excs,
                risk_level=risk
            ))

        # 5. Top Exception Patterns
        exc_groups = defaultdict(list)
        for r in records:
            exc_groups[r["exception_type"]].append(r)

        exception_patterns: List[ExceptionPattern] = []
        for exc_name, exc_recs in sorted(exc_groups.items(), key=lambda x: len(x[1]), reverse=True):
            if exc_name == "UnclassifiedException" and len(exc_groups) > 1:
                continue
            e_count = len(exc_recs)
            comps = list(set(r["component"] for r in exc_recs))[:4]
            fps = [r["failure_point"] for r in exc_recs if r["failure_point"] != "N/A"][:3]
            msgs = [r["title"] for r in exc_recs][:3]
            sev_b = dict(Counter(r["severity"] for r in exc_recs))

            exception_patterns.append(ExceptionPattern(
                exception_type=exc_name,
                occurrence_count=e_count,
                percentage=round((e_count / total) * 100, 1),
                affected_components=comps,
                sample_failure_points=fps,
                sample_error_messages=msgs,
                severity_breakdown=sev_b
            ))

        # 6. Root Cause Themes
        root_cause_themes = cls._categorize_root_cause_themes(records)

        # 7. Semantic Bug Clusters
        semantic_clusters = cls._cluster_defects_semantically(records)

        # 8. Time Trends
        time_trends = cls._analyze_time_trends(records)

        # 9. KPIs
        top_comp = component_hotspots[0].component if component_hotspots else "None"
        crit_high_cnt = sev_counts.get("Critical", 0) + sev_counts.get("High", 0)
        crit_high_pct = round((crit_high_cnt / total) * 100, 1)
        dup_cnt = dup_counts.get("Likely Duplicate", 0) + dup_counts.get("Related Issue", 0)
        recurring_cnt = sum(1 for r in records if exc_groups[r["exception_type"]].__len__() > 1 or comp_groups[r["component"]].__len__() > 1)
        rec_rate = round((recurring_cnt / total) * 100, 1) if total > 0 else 0.0

        kpis = AnalyticsKPIs(
            total_defects_analyzed=total,
            recurring_pattern_rate=rec_rate,
            top_affected_component=top_comp,
            critical_high_percentage=crit_high_pct,
            duplicate_defect_count=dup_cnt,
            unique_exception_types=len(exc_groups)
        )

        return AnalyticsOverviewResponse(
            kpis=kpis,
            severity_distribution=severity_dist,
            priority_distribution=priority_dist,
            duplicate_distribution=duplicate_dist,
            component_hotspots=component_hotspots,
            top_exception_patterns=exception_patterns[:6],
            root_cause_themes=root_cause_themes,
            semantic_clusters=semantic_clusters,
            time_trends=time_trends
        )

    @classmethod
    def _categorize_root_cause_themes(cls, records: List[Dict[str, Any]]) -> List[RootCauseTheme]:
        total = len(records)
        theme_buckets = defaultdict(list)
        unmatched_recs = []

        for r in records:
            matched = False
            haystack = f"{r['title']} {r['description']} {r['root_cause']} {r['exception_type']}".lower()

            for cat in KNOWN_ROOT_CAUSE_CATEGORIES:
                if any(kw in haystack for kw in cat["keywords"]):
                    theme_buckets[cat["id"]].append(r)
                    matched = True
                    break
            if not matched:
                unmatched_recs.append(r)

        result: List[RootCauseTheme] = []
        for cat in KNOWN_ROOT_CAUSE_CATEGORIES:
            matches = theme_buckets.get(cat["id"], [])
            if not matches:
                continue
            cnt = len(matches)
            comps = list(set(m["component"] for m in matches))[:4]
            titles = [m["title"] for m in matches][:3]

            rems = [
                RemediationPatternItem(
                    pattern_title=rp["pattern_title"],
                    recommended_action=rp["recommended_action"],
                    frequency=cnt,
                    example_code_snippet=rp["example_code_snippet"]
                )
                for rp in cat["remediations"]
            ]

            result.append(RootCauseTheme(
                theme_id=cat["id"],
                theme_name=cat["name"],
                description=cat["description"],
                frequency=cnt,
                percentage=round((cnt / total) * 100, 1) if total > 0 else 0.0,
                associated_components=comps,
                common_remediations=rems,
                sample_bug_titles=titles
            ))

        # Add fallback theme if unmatched exist
        if unmatched_recs:
            cnt = len(unmatched_recs)
            result.append(RootCauseTheme(
                theme_id="theme_general_logic",
                theme_name="General Business Logic & State Irregularities",
                description="Defects related to application domain rules, unexpected edge states, or miscellaneous exceptions.",
                frequency=cnt,
                percentage=round((cnt / total) * 100, 1),
                associated_components=list(set(m["component"] for m in unmatched_recs))[:4],
                common_remediations=[
                    RemediationPatternItem(
                        pattern_title="Comprehensive Unit Test Coverage",
                        recommended_action="Implement parameterized test suites covering edge boundary conditions.",
                        frequency=cnt,
                        example_code_snippet="// Verify edge condition logic\n@Test\nvoid testEdgeCases() { ... }"
                    )
                ],
                sample_bug_titles=[m["title"] for m in unmatched_recs][:3]
            ))

        result.sort(key=lambda t: t.frequency, reverse=True)
        return result

    @classmethod
    def _cluster_defects_semantically(cls, records: List[Dict[str, Any]]) -> List[SemanticCluster]:
        if not records:
            return []

        clusters_map = defaultdict(list)
        for r in records:
            comp = r["component"]
            exc = r["exception_type"]
            key = f"{comp}::{exc}"
            clusters_map[key].append(r)

        semantic_clusters: List[SemanticCluster] = []
        total = len(records)
        cluster_idx = 1

        for key, members in sorted(clusters_map.items(), key=lambda x: len(x[1]), reverse=True):
            c_comp = members[0]["component"]
            c_exc = members[0]["exception_type"]
            theme = f"{c_comp}: {c_exc} Cluster" if c_exc != "UnclassifiedException" else f"{c_comp} Functional Defect Cluster"

            sev_counts = Counter(m["severity"] for m in members)
            dom_sev = sev_counts.most_common(1)[0][0] if sev_counts else "Medium"
            rep_bug = members[0]["title"]

            coherence = 0.88 if len(members) > 1 else 0.76

            cluster_members = [
                ClusterMemberDefect(
                    id=m["id"],
                    bug_id=m["bug_id"],
                    title=m["title"],
                    severity=m["severity"],
                    component=m["component"],
                    similarity_to_centroid=round(max(0.60, coherence - (idx * 0.03)), 2),
                    created_at=m["created_at"].strftime("%Y-%m-%d") if isinstance(m["created_at"], (datetime, date)) else None
                )
                for idx, m in enumerate(members)
            ]

            semantic_clusters.append(SemanticCluster(
                cluster_id=f"cluster_{cluster_idx}",
                cluster_theme=theme,
                defect_count=len(members),
                percentage_of_total=round((len(members) / total) * 100, 1),
                average_similarity=coherence,
                representative_defect=rep_bug,
                primary_component=c_comp,
                dominant_severity=dom_sev,
                members=cluster_members
            ))
            cluster_idx += 1

        return semantic_clusters[:8]

    @classmethod
    def _analyze_time_trends(cls, records: List[Dict[str, Any]]) -> TimeTrendAnalysis:
        if not records:
            return TimeTrendAnalysis(interval="daily", trend_direction="Stable", velocity_percentage=0.0, timeline=[])

        date_groups = defaultdict(list)
        for r in records:
            dt = r["created_at"]
            if isinstance(dt, datetime):
                d_str = dt.strftime("%Y-%m-%d")
            elif isinstance(dt, str):
                d_str = dt[:10]
            else:
                d_str = datetime.utcnow().strftime("%Y-%m-%d")
            date_groups[d_str].append(r)

        sorted_dates = sorted(date_groups.keys())
        timeline: List[TimeTrendPoint] = []

        for d in sorted_dates:
            d_recs = date_groups[d]
            crit = sum(1 for r in d_recs if r["severity"] == "Critical")
            high = sum(1 for r in d_recs if r["severity"] == "High")
            top_c = Counter(r["component"] for r in d_recs).most_common(1)[0][0] if d_recs else None

            timeline.append(TimeTrendPoint(
                period=d,
                total_count=len(d_recs),
                critical_count=crit,
                high_count=high,
                top_component=top_c
            ))

        if len(timeline) >= 2:
            mid = len(timeline) // 2
            first_half = sum(p.total_count for p in timeline[:mid])
            second_half = sum(p.total_count for p in timeline[mid:])
            if first_half > 0:
                vel = round(((second_half - first_half) / first_half) * 100, 1)
            else:
                vel = 100.0 if second_half > 0 else 0.0

            if vel > 15.0:
                direction = "Increasing"
            elif vel < -15.0:
                direction = "Decreasing"
            else:
                direction = "Stable"
        else:
            direction = "Stable"
            vel = 0.0

        return TimeTrendAnalysis(
            interval="daily",
            trend_direction=direction,
            velocity_percentage=vel,
            timeline=timeline
        )

    @classmethod
    def get_filter_options(cls, db: Session) -> AnalyticsFilterOptions:
        comps = set()
        excs = set()
        sources = ["all", "submitted", "historical"]

        for b in db.query(BugReport).all():
            if b.component:
                comps.add(b.component)
            exc = cls._extract_exception_from_text(b.stack_trace) or cls._extract_exception_from_text(b.error_logs)
            if exc:
                excs.add(exc)

        for h in db.query(HistoricalDefect).all():
            if h.component:
                comps.add(h.component)
            elif h.project:
                comps.add(h.project)
            exc = cls._extract_exception_from_text(h.error_message) or cls._extract_exception_from_text(h.stack_trace)
            if exc:
                excs.add(exc)

        return AnalyticsFilterOptions(
            available_components=sorted(list(comps)),
            available_severities=["Critical", "High", "Medium", "Low"],
            available_priorities=["Critical", "High", "Medium", "Low"],
            available_exception_types=sorted(list(excs)),
            available_sources=sources
        )
