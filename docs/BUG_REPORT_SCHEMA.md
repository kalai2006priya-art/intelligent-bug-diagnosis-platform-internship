# Bug Report Schema Specification

## 1. Overview
The Bug Report Schema defines the standardized contract for bugs submitted by users, persisted in the relational database, and processed across the multi-agent pipeline.

---

## 2. JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BugReport",
  "type": "object",
  "properties": {
    "bug_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for the bug report (UUIDv4)."
    },
    "user_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier of the user who submitted the report."
    },
    "title": {
      "type": "string",
      "minLength": 5,
      "maxLength": 255,
      "description": "Concise summary of the defect."
    },
    "description": {
      "type": "string",
      "minLength": 10,
      "description": "Detailed description of observed symptoms and reproduction steps."
    },
    "stack_trace": {
      "type": ["string", "null"],
      "description": "Raw runtime execution stack trace (optional)."
    },
    "error_logs": {
      "type": ["string", "null"],
      "description": "Surrounding operational logs or console output (optional)."
    },
    "component": {
      "type": ["string", "null"],
      "maxLength": 100,
      "description": "User-identified or agent-inferred system component (optional)."
    },
    "environment": {
      "type": ["string", "null"],
      "maxLength": 255,
      "description": "Operating system, runtime environment, container or browser specs (optional)."
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp of submission."
    },
    "status": {
      "type": "string",
      "enum": ["Submitted", "Analyzing", "Diagnosed", "Failed"],
      "default": "Submitted",
      "description": "Current processing state of the bug report."
    }
  },
  "required": ["bug_id", "user_id", "title", "description", "created_at", "status"]
}
```

---

## 3. Relational Database Mapping (SQLAlchemy)

| Column Name | SQL Type | Nullable | Primary Key | Foreign Key | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | No | Yes | - | UUIDv4 string |
| `user_id` | `VARCHAR(36)` | No | No | `users.id` | Cascades on user deletion |
| `title` | `VARCHAR(255)` | No | No | - | Indexed for search |
| `description` | `TEXT` | No | No | - | Primary text content |
| `stack_trace` | `TEXT` | Yes | No | - | Raw stack trace text |
| `error_logs` | `TEXT` | Yes | No | - | Operational log text |
| `component` | `VARCHAR(100)` | Yes | No | - | Module label |
| `environment` | `VARCHAR(255)` | Yes | No | - | Runtime specs |
| `status` | `VARCHAR(20)` | No | No | - | State enum |
| `created_at` | `DATETIME` | No | No | - | UTC datetime |
| `updated_at` | `DATETIME` | No | No | - | Auto-updated UTC datetime |

---

## 4. API Request & Response Schemas (Pydantic)

### Create Bug Request (`BugCreate`)
```python
class BugCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    stack_trace: Optional[str] = None
    error_logs: Optional[str] = None
    component: Optional[str] = None
    environment: Optional[str] = None
```

### Bug Details Response (`BugResponse`)
```python
class BugResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    stack_trace: Optional[str]
    error_logs: Optional[str]
    component: Optional[str]
    environment: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
```
