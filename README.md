# Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance

## Project Overview

This project focuses on developing an intelligent platform for software bug diagnosis and fix recommendation.

The system accepts bug reports, stack traces, and error logs from users. It analyzes the submitted information, retrieves similar historical defects using semantic similarity and a Retrieval-Augmented Generation (RAG) pipeline, and provides possible root-cause analysis and fix recommendations.

## Main Objectives

- Accept bug reports, stack traces, and error logs
- Process and validate submitted bug information
- Find similar defects from historical bug reports
- Use semantic similarity and vector search for defect retrieval
- Analyze possible root causes of software defects
- Recommend possible fixes based on retrieved historical knowledge
- Build a historical defect knowledge base using public datasets
- Support AI-agent-based bug diagnosis

## Main Modules

1. Bug Submission Module
2. Bug Report Processing Module
3. Historical Defect Knowledge Base
4. Data Cleaning and Standardization
5. Dataset Chunking Pipeline
6. Embedding Generation
7. FAISS Vector Search
8. RAG Retrieval Pipeline
9. AI Agent Layer
10. Structured Diagnosis
11. Fix Recommendation

## AI Agent Layer

The platform is designed with multiple specialized agents:

- **Triage Agent** – performs initial classification and prioritization of the reported bug
- **Log Analysis Agent** – analyzes stack traces and error logs
- **Historical Defect Retrieval** – retrieves relevant historical defects using semantic similarity
- **Duplicate Detection Agent** – identifies potentially duplicate or highly similar historical defects
- **Root Cause Agent** – identifies possible causes of the defect
- **Remediation Agent** – provides possible fix or remediation recommendations

An Agent Orchestrator coordinates the execution and information flow between these specialized agents.

## Historical Defect Knowledge Base

The historical defect knowledge base is developed using public software defect datasets from:

- Mozilla
- Apache
- Eclipse

The historical bug reports are cleaned, standardized, divided into manageable chunks, converted into vector embeddings, and indexed using FAISS for semantic retrieval.

### Current Dataset Processing Pipeline

```text
Historical Defect Datasets
        |
        v
Dataset Inspection
        |
        v
Data Cleaning & Standardization
        |
        v
Dataset Chunking
        |
        v
Embedding Generation
        |
        v
FAISS Vector Indexing
        |
        v
Semantic Similarity Retrieval
```
