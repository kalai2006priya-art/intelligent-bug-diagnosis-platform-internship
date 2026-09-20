# Historical Defect Knowledge Base Schema Specification

## 1. Overview
The Historical Defect Knowledge Base stores cleaned, normalized, and chunked defects from public repositories (**Mozilla**, **Apache**, and **Eclipse**). Each record supports both relational storage and semantic vector embeddings in ChromaDB.

---

## 2. Standardized Historical Defect Record Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HistoricalDefectRecord",
  "type": "object",
  "properties": {
    "chunk_id": {
      "type": "string",
      "description": "Unique identifier for the specific indexed chunk (e.g., APACHE-1420-chunk-01)."
    },
    "dataset_source": {
      "type": "string",
      "enum": ["Mozilla", "Apache", "Eclipse"],
      "description": "Originating defect repository."
    },
    "project": {
      "type": "string",
      "description": "Subproject within repository (e.g., Firefox, Spark, Core, JDT)."
    },
    "bug_id": {
      "type": "string",
      "description": "Original issue identifier from source tracker (e.g., 104291)."
    },
    "title": {
      "type": "string",
      "description": "Original defect summary."
    },
    "description": {
      "type": "string",
      "description": "Full or chunked defect description."
    },
    "comments": {
      "type": "string",
      "description": "Developer discussion threads or resolution notes."
    },
    "stack_trace": {
      "type": "string",
      "description": "Attached stack trace or crash log snippet."
    },
    "error_message": {
      "type": "string",
      "description": "Parsed exception or error string."
    },
    "component": {
      "type": "string",
      "description": "Subsystem label in the source tracker."
    },
    "severity": {
      "type": "string",
      "description": "Recorded severity in source repository."
    },
    "priority": {
      "type": "string",
      "description": "Recorded priority in source repository."
    },
    "resolution": {
      "type": "string",
      "description": "Outcome status (e.g., FIXED, RESOLVED, DUPLICATE)."
    },
    "status": {
      "type": "string",
      "description": "Defect status (e.g., CLOSED, VERIFIED)."
    },
    "source_reference": {
      "type": "string",
      "description": "URL or commit identifier referencing the original fix."
    },
    "chunk_type": {
      "type": "string",
      "enum": ["summary", "description", "stack_trace", "resolution", "combined"],
      "description": "Type of content encapsulated in this chunk."
    }
  },
  "required": [
    "chunk_id",
    "dataset_source",
    "bug_id",
    "title",
    "description"
  ]
}
```

---

## 3. ChromaDB Vector Metadata Schema

When storing defect embeddings in ChromaDB, the document text contains the semantic representation, and metadata is indexed for fast pre-filtering:

| Chroma Metadata Field | Data Type | Purpose |
| :--- | :--- | :--- |
| `chunk_id` | `string` | Unique chunk key |
| `source` | `string` | Repository (`Mozilla`, `Apache`, `Eclipse`) |
| `project` | `string` | Subproject identifier |
| `bug_id` | `string` | Defect tracker issue ID |
| `component` | `string` | Subsystem label |
| `resolution` | `string` | Verification outcome (`FIXED`, etc.) |
| `chunk_type` | `string` | `description`, `stack_trace`, or `combined` |

---

## 4. Kaggle Dataset Column Mapping & Normalization

Public Kaggle datasets for Mozilla, Apache, and Eclipse exhibit heterogeneous schemas. The ingestion pipeline (`scripts/process_datasets.py`) standardizes these variations:

| Standard Target Field | Mozilla (Bugzilla) Variants | Apache (Jira) Variants | Eclipse (Bugzilla) Variants |
| :--- | :--- | :--- | :--- |
| `bug_id` | `Bug ID`, `bug_id`, `id` | `Issue key`, `Issue id`, `key` | `bug_id`, `id`, `Issue_id` |
| `title` | `Summary`, `Short Description` | `Summary`, `Title` | `Summary`, `short_desc` |
| `description` | `Description`, `Long Description` | `Description`, `body` | `Description`, `long_desc` |
| `component` | `Component`, `product_component` | `Component/s`, `component` | `Component`, `component` |
| `severity` | `Severity`, `bug_severity` | `Priority`, `Issue Type` | `Severity`, `bug_severity` |
| `priority` | `Priority` | `Priority` | `Priority` |
| `resolution` | `Resolution` | `Resolution`, `Status` | `Resolution` |
| `comments` | `Comments`, `discussion` | `Comments` | `Comments` |
