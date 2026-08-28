# Historical Defect Knowledge Base Schema

The Historical Defect Knowledge Base stores information from previously reported software defects.

The knowledge base will support semantic retrieval, duplicate detection, root cause analysis, and fix recommendation.

## Historical Defect Record

| Field | Description |
|---|---|
| Defect ID | Unique identifier of the historical defect |
| Source | Original dataset or project source |
| Project | Software project associated with the defect |
| Component | Software component affected |
| Summary | Short description of the defect |
| Description | Detailed defect description |
| Steps to Reproduce | Steps used to reproduce the defect |
| Stack Trace | Available execution or error information |
| Error Logs | Available log information |
| Severity | Impact level of the defect |
| Priority | Priority assigned to the defect |
| Status | Current status of the defect |
| Resolution | Resolution applied to the defect |
| Comments | Relevant discussion or additional information |
| Created Date | Date when the defect was reported |
| Resolved Date | Date when the defect was resolved |

## Knowledge Base Processing

Historical defect data will pass through the following stages:

Raw Dataset
→ Data Cleaning
→ Data Standardization
→ Chunking
→ Embedding Generation
→ Vector Database Indexing
→ Semantic Retrieval

## Chunking Strategy

Large historical defect records may be divided into smaller meaningful chunks.

Possible chunks include:

- Bug Description
- Steps to Reproduce
- Stack Trace
- Error Logs
- Developer Comments
- Resolution / Fix Information

Each chunk will retain relevant metadata such as defect ID, project, component, and source.

## Vector Database Metadata

Each embedded chunk will be associated with metadata including:

- Defect ID
- Source
- Project
- Component
- Chunk Type
- Original Record Reference

This metadata will help identify and present the source of retrieved historical defects.

## Retrieval Process

When a new bug is submitted:

1. The submitted bug is processed.
2. Relevant text is converted into an embedding.
3. The embedding is searched against the historical defect vectors.
4. Similar defect chunks are retrieved.
5. Retrieved information is passed to the RAG pipeline.
6. The retrieved context is used by the AI agents for diagnosis and remediation.

## Purpose

The knowledge base provides historical software defect information that can be retrieved when analyzing new bug reports.

It is intended to support evidence-based diagnosis rather than relying only on the general knowledge of the language model.
