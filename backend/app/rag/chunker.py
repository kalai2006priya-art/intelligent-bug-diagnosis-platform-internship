import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """Sanitize raw bug text, strip HTML tags, and normalize whitespace."""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]+>', ' ', text)
    # Normalize multiple whitespace and linebreaks
    clean = re.sub(r'[ \t]+', ' ', clean)
    clean = re.sub(r'\n\s*\n', '\n\n', clean)
    return clean.strip()

def chunk_historical_bug(record: Dict[str, Any], max_chunk_chars: int = 1000) -> List[Dict[str, Any]]:
    """
    Splits a historical bug record into semantic chunks with associated metadata.
    Avoids blindly dumping the entire record into one chunk.
    """
    chunks = []
    bug_id = str(record.get("bug_id", "UNKNOWN"))
    source = record.get("dataset_source", "General")
    project = record.get("project", "")
    component = record.get("component", "")
    resolution = record.get("resolution", "")
    title = clean_text(record.get("title", ""))
    description = clean_text(record.get("description", ""))
    stack_trace = clean_text(record.get("stack_trace", ""))
    comments = clean_text(record.get("comments", ""))

    base_metadata = {
        "source": source,
        "project": project,
        "bug_id": bug_id,
        "component": component or "General",
        "resolution": resolution or "UNRESOLVED",
        "title": title[:200]
    }

    # 1. Primary Summary & Description Chunk
    desc_content = f"Bug ID: {bug_id} [{source} / {project}]\nTitle: {title}\nComponent: {component}\nDescription: {description}"
    if len(desc_content) > max_chunk_chars:
        # Split into smaller slices
        for idx, i in enumerate(range(0, len(desc_content), max_chunk_chars - 100)):
            chunk_slice = desc_content[i:i + max_chunk_chars]
            chunks.append({
                "chunk_id": f"{source}-{bug_id}-desc-{idx}",
                "text": chunk_slice,
                "metadata": {**base_metadata, "chunk_type": "description"}
            })
    else:
        chunks.append({
            "chunk_id": f"{source}-{bug_id}-desc-0",
            "text": desc_content,
            "metadata": {**base_metadata, "chunk_type": "description"}
        })

    # 2. Stack Trace Chunk (if available)
    if stack_trace and len(stack_trace) > 20:
        trace_content = f"Bug ID: {bug_id} [{source}]\nTitle: {title}\nRuntime Stack Trace:\n{stack_trace}"
        chunks.append({
            "chunk_id": f"{source}-{bug_id}-trace-0",
            "text": trace_content[:max_chunk_chars],
            "metadata": {**base_metadata, "chunk_type": "stack_trace"}
        })

    # 3. Resolution & Comments Chunk (if available)
    if comments and len(comments) > 20:
        res_content = f"Bug ID: {bug_id} [{source}]\nTitle: {title}\nResolution: {resolution}\nFix Details & Notes:\n{comments}"
        chunks.append({
            "chunk_id": f"{source}-{bug_id}-resolution-0",
            "text": res_content[:max_chunk_chars],
            "metadata": {**base_metadata, "chunk_type": "resolution"}
        })

    return chunks
