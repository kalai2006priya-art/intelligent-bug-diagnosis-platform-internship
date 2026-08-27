# Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance

## Project Overview

This project focuses on developing an intelligent platform for software bug diagnosis and fix recommendation.

The system accepts bug reports, stack traces, and error logs from users. It analyzes the submitted information, retrieves similar historical defects using semantic search and a RAG pipeline, and provides possible root-cause analysis and fix recommendations.

## Main Objectives

- Accept bug reports, stack traces, and error logs
- Process and validate submitted bug information
- Find similar defects from historical bug reports
- Use semantic similarity and vector search for defect retrieval
- Analyze possible root causes of software defects
- Recommend possible fixes based on retrieved knowledge
- Build a historical defect knowledge base using public datasets

## Main Modules

1. Bug Submission Module
2. Bug Report Processing Module
3. Historical Defect Knowledge Base
4. Data Cleaning and Chunking Pipeline
5. Embedding Generation
6. Vector Database and Semantic Search
7. RAG Retrieval Pipeline
8. AI Agent Layer
9. Structured Diagnosis
10. Fix Recommendation

## AI Agent Layer

The platform is designed with multiple specialized agents:

- Triage Agent – performs initial classification and prioritization of the reported bug
- Log Analysis Agent – analyzes stack traces and error logs
- Root Cause Agent – identifies possible causes of the defect
- Duplicate Detection Agent – finds potentially duplicate or similar historical defects
- Remediation Agent – provides possible fix or remediation recommendations

An Agent Orchestrator coordinates the execution and information flow between these agents.

## Historical Defect Knowledge Base

The historical defect knowledge base will be developed using public bug datasets from:

- Mozilla
- Apache
- Eclipse

The historical bug reports will be cleaned, standardized, chunked, converted into embeddings, and indexed in a vector database for semantic retrieval.

## RAG Pipeline

The Retrieval-Augmented Generation (RAG) pipeline retrieves relevant historical defects based on the submitted bug information.

The retrieved context is provided to the language model and AI agent layer to support diagnosis and fix recommendation.

## Technology Stack

### Frontend
- React.js

### Backend
- Python
- FastAPI

### AI / Machine Learning
- Python
- Sentence Transformers
- Semantic Similarity
- Embeddings
- Large Language Model (LLM)

### RAG
- LangChain
- Retrieval-Augmented Generation (RAG)

### Vector Database
- ChromaDB

### Database
- PostgreSQL

### Development & Version Control
- Git
- GitHub

### System Architecture
- Draw.io

## Project Architecture

The system architecture describes the flow from bug submission and processing to historical defect retrieval, AI-agent-based diagnosis, and fix recommendation.

![System Architecture](System_Architecture.png)

## Project Status

**Milestone 1 - In Progress**

Current focus:

- Understanding defect analysis workflows
- Studying RAG architecture and semantic similarity
- Designing system architecture and agent responsibilities
- Developing the Bug Submission Module
- Building the Historical Defect Knowledge Base
