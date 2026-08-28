# Bug Report Schema

The Bug Report Schema defines the information that will be collected and stored for each submitted software defect.

## Proposed Bug Report Fields

| Field | Description |
|---|---|
| Bug ID | Unique identifier for the submitted bug |
| Title | Short summary of the defect |
| Description | Detailed description of the problem |
| Steps to Reproduce | Steps required to reproduce the defect |
| Expected Result | Expected system behavior |
| Actual Result | Actual behavior observed |
| Environment | Operating system, browser, application version, etc. |
| Severity | Impact level of the defect |
| Priority | Urgency of resolving the defect |
| Stack Trace | Technical execution information |
| Error Logs | Error and application logs |
| Attachments | Uploaded bug reports or log files |
| Status | Current state of the defect |
| Created At | Date and time of submission |

## Historical Defect Metadata

Historical defects retrieved from public datasets may contain additional information such as:

- Original bug identifier
- Product or project
- Component
- Bug summary
- Bug description
- Comments
- Severity
- Priority
- Status
- Resolution
- Fix information
- Creation date
- Resolution date

## Data Flow

Bug Submission
→ Validation
→ Bug Report Storage
→ Bug Processing
→ Embedding Generation
→ Historical Defect Retrieval
→ Agent Diagnosis

## Purpose

The schema provides a consistent structure for storing and processing newly submitted bugs and historical defect information. This structured information will be used by the RAG pipeline and specialized AI agents for bug diagnosis and fix recommendation.
