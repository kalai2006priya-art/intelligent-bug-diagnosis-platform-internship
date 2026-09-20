import logging
from typing import Dict, Any, List, Optional
from app.config import settings
from app.agents.base_agent import BaseAgent
from app.schemas.diagnosis import DuplicateDetectionResult, DuplicateMatchItem

logger = logging.getLogger(__name__)

class DuplicateDetectionAgent(BaseAgent):
    agent_name: str = "Duplicate Detection Agent"

    async def analyze(
        self,
        bug_title: str,
        bug_description: str,
        retrieved_defects: List[Dict[str, Any]],
        submitted_matches: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates semantic similarity between the submitted bug and historical + platform defects
        using configurable thresholds.
        """
        return self.heuristic_analyze(bug_title, bug_description, retrieved_defects, submitted_matches)

    def heuristic_analyze(
        self,
        bug_title: str,
        bug_description: str,
        retrieved_defects: List[Dict[str, Any]],
        submitted_matches: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        # Check for insufficient text evidence
        combined_text = f"{bug_title} {bug_description}".strip()
        if len(combined_text) < 15:
            return {
                "status": "Insufficient Evidence",
                "matches": [],
                "reasoning": "Insufficient Evidence: Defect description is too brief to perform semantic duplicate comparison."
            }

        # Combine historical vector matches and submitted bug matches
        all_candidates = []

        for d in (retrieved_defects or []):
            meta = d.get("metadata", {})
            sim = float(d.get("similarity", 0.0))
            all_candidates.append({
                "bug_id": str(meta.get("bug_id", "HIST-BUG")),
                "similarity": sim,
                "title": meta.get("title", "Historical Bug Record"),
                "source": meta.get("source", "Historical Repo"),
                "project": meta.get("project", "General"),
                "component": meta.get("component", "General"),
                "resolution_summary": meta.get("resolution", "Referenced historical issue")
            })

        for s in (submitted_matches or []):
            all_candidates.append({
                "bug_id": s.get("bug_id", "PLATFORM-BUG"),
                "similarity": float(s.get("similarity", 0.0)),
                "title": s.get("title", "Previously Submitted Platform Bug"),
                "source": "Platform User Submissions",
                "project": "Current Platform",
                "component": s.get("component", "General"),
                "resolution_summary": s.get("status", "Previously Submitted")
            })

        # Sort candidates descending by similarity
        all_candidates.sort(key=lambda x: x["similarity"], reverse=True)

        # Threshold evaluation
        duplicate_thresh = settings.SIMILARITY_THRESHOLD_DUPLICATE
        related_thresh = settings.SIMILARITY_THRESHOLD_RELATED

        filtered_matches = []
        status = "New / Unmatched"
        reasoning = "No existing defect in historical repositories or platform records exceeded the similarity threshold."

        if all_candidates:
            top_sim = all_candidates[0]["similarity"]
            # Include candidates above related threshold
            filtered_matches = [
                c for c in all_candidates if c["similarity"] >= related_thresh
            ][:5]

            if top_sim >= duplicate_thresh:
                status = "Likely Duplicate"
                reasoning = (
                    f"Top match '{all_candidates[0]['bug_id']}' exhibited a similarity score of {top_sim:.2f}, "
                    f"exceeding the {duplicate_thresh:.2f} threshold for duplicate classification."
                )
            elif top_sim >= related_thresh:
                status = "Related Issue"
                reasoning = (
                    f"Top match '{all_candidates[0]['bug_id']}' showed a similarity score of {top_sim:.2f}, "
                    f"exceeding the {related_thresh:.2f} threshold for related defects sharing similar symptoms or components."
                )
            else:
                status = "New / Unmatched"
                reasoning = (
                    f"Highest observed similarity was {top_sim:.2f}, falling below the related issue threshold ({related_thresh:.2f}). "
                    "Classified as a new, unique defect."
                )
        else:
            status = "New / Unmatched"
            reasoning = "Knowledge base is currently empty or contains no related defect vectors."

        return {
            "status": status,
            "matches": filtered_matches,
            "reasoning": reasoning
        }
