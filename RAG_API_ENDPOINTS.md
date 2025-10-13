# RAG API Endpoints Documentation

## Overview

This document describes the CNZ RAG (Retrieval-Augmented Generation) API endpoints available for querying PDF documents, managing notes, and batch processing document collections. The RAG system enables intelligent semantic search across academic papers and city data documents.

## Server Endpoints

### Production Servers
- **CNZ CL Server**: `cnz-cl.icmserver007.com`
- **CNZ RAG Server**: `cnz-rag.icmserver007.com`

### Local Development
- **Main API**: `http://localhost:8000`
- **Standalone RAG API**: `http://localhost:8001`

---

## API Routes

### 1. Health Check / Root
```bash
curl http://localhost:8000/
```
**Purpose**: Verify the API is running and check basic service information.

---

### 2. Query PDFs (RAG Search)
```bash
curl -X POST http://localhost:8000/api/query-pdfs \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the crime rate in Bristol?",
    "mode": "hybrid"
  }'
```
**Purpose**: Perform semantic search across indexed PDF documents using RAG technology.
- **Query Modes**:
  - `hybrid`: Combines semantic and keyword search
  - `semantic`: Pure vector similarity search
  - `keyword`: Traditional text matching

**Use Cases**:
- Find relevant research papers on specific topics
- Extract city statistics and metrics
- Answer questions based on document content

---

### 3. Save Note
```bash
curl -X POST http://localhost:8000/api/note \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bristol crime rate decreased 5% in 2023 - Quality of Life survey"
  }'
```
**Purpose**: Store research notes and findings for later retrieval.

---

### 4. Search Notes
```bash
curl "http://localhost:8000/api/notes/search?pattern=bristol"
```
**Purpose**: Search saved notes using pattern matching.

---

### 5. Memory Status
```bash
curl http://localhost:8000/api/memory
```
**Purpose**: Monitor system memory usage and performance metrics.

---

### 6. Health Check (Detailed)
```bash
curl http://localhost:8000/health
```
**Purpose**: Comprehensive health status of all system components.

---

### 7. RAG Index Statistics
```bash
curl http://localhost:8000/api/index/stats
```
**Purpose**: Get statistics about the RAG vector database index.
- Number of indexed documents
- Vector dimensions
- Index size and performance metrics

**Critical for Data Analysts**: Use this to understand the scope and coverage of available research data.

---

### 8. Start Batch Processing
```bash
curl -X POST http://localhost:8000/api/batch/start \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "/Users/boov/CNZ_ALL_CITIES",
    "max_workers": 2,
    "file_types": ["pdf"]
  }'
```
**Purpose**: Process large collections of PDF documents for RAG indexing.
- **folder_path**: Directory containing PDFs to process
- **max_workers**: Number of parallel processing threads
- **file_types**: File extensions to process (default: ["pdf"])

**Use Cases**:
- Index new academic paper collections
- Update city data document repositories
- Build searchable knowledge bases

---

### 9. Get Batch Job Status
```bash
curl http://localhost:8000/api/batch/status/batch_2025-10-03_11-38-06
```
**Purpose**: Monitor progress of a specific batch processing job.

---

### 10. List All Batch Jobs
```bash
curl http://localhost:8000/api/batch/status
```
**Purpose**: View all batch processing jobs and their current status.

---

### 11. Interactive API Documentation (Swagger UI)
```bash
# Open in browser:
open http://localhost:8000/docs
```
**Purpose**: Interactive API documentation with built-in testing interface.

---

## Standalone RAG Manual API

### Purpose
The `rag_manual_api.py` provides a standalone interface for RAG features that can be run independently of the main `api_server.py`. This is useful for:
- Dedicated RAG processing workloads
- Isolated testing and development
- Running RAG services on separate infrastructure

### Running Standalone API
```bash
# Run standalone RAG API (port 8001)
uv run python rag_manual_api.py

# Test it
uv run python test_rag_manual.py

# Or use curl
curl http://localhost:8001/api/index/stats | python3 -m json.tool
```

### Key Features
- Query PDFs via RAG
- Get index statistics
- Start/monitor batch processing
- Memory monitoring
- Independent from main api_server.py
- Runs on port 8001 (different from main API)

---

## Quick Test Script

Save this as `test_all_routes.sh`:

```bash
#!/bin/bash

echo "=== 1. Root ===" && curl -s http://localhost:8000/ | python3 -m json.tool

echo -e "\n=== 2. Memory Status ===" && curl -s http://localhost:8000/api/memory | python3 -m json.tool

echo -e "\n=== 3. Index Stats ===" && curl -s http://localhost:8000/api/index/stats | python3 -m json.tool

echo -e "\n=== 4. Save Note ===" && curl -s -X POST http://localhost:8000/api/note \
  -H "Content-Type: application/json" \
  -d '{"text": "Test note from curl"}' | python3 -m json.tool

echo -e "\n=== 5. Search Notes ===" && curl -s "http://localhost:8000/api/notes/search?pattern=test" | python3 -m json.tool

echo -e "\n=== 6. Query PDFs ===" && curl -s -X POST http://localhost:8000/api/query-pdfs \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the population of Bristol?", "mode": "hybrid"}' | python3 -m json.tool

echo -e "\n=== 7. List Batch Jobs ===" && curl -s http://localhost:8000/api/batch/status | python3 -m json.tool
```

---

## Data Analyst Use Cases

### 1. Research Academic Papers
Use the RAG query endpoint to find relevant research papers on specific topics:
```bash
curl -X POST http://localhost:8000/api/query-pdfs \
  -H "Content-Type: application/json" \
  -d '{"query": "Net Zero carbon reduction strategies", "mode": "hybrid"}'
```

### 2. Extract City Statistics
Query indexed city data documents for specific metrics:
```bash
curl -X POST http://localhost:8000/api/query-pdfs \
  -H "Content-Type: application/json" \
  -d '{"query": "Bristol population demographics 2023", "mode": "semantic"}'
```

### 3. Monitor Index Coverage
Check RAG index statistics to understand data availability:
```bash
curl http://localhost:8000/api/index/stats | python3 -m json.tool
```

### 4. Batch Process New Data Sources
Index new document collections for analysis:
```bash
curl -X POST http://localhost:8000/api/batch/start \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "/path/to/new/papers",
    "max_workers": 4,
    "file_types": ["pdf"]
  }'
```

### 5. Build Research Notes
Save findings and insights for knowledge management:
```bash
curl -X POST http://localhost:8000/api/note \
  -H "Content-Type: application/json" \
  -d '{"text": "Key finding: Solar adoption rates correlate with local policy incentives"}'
```

---

## Integration with Data Analysis Workflows

The Data Analyst Agent can leverage these RAG API endpoints to:

1. **Automated Research**: Query academic papers and extract relevant findings
2. **Data Validation**: Cross-reference city statistics with source documents
3. **Report Generation**: Pull evidence-based insights from indexed knowledge base
4. **Continuous Learning**: Index new papers and data sources as they become available
5. **Knowledge Management**: Build searchable repositories of research notes and findings

---

## Related Files

- **Main API Server**: `/Users/boov/cnz_claude_rag_all/api_server.py`
- **Standalone RAG API**: `rag_manual_api.py`
- **Test Script**: `test_rag_manual.py`
- **Documentation**: This file

---

## Technical Notes

- **Vector Database**: Uses ChromaDB or similar for semantic search
- **Embeddings**: OpenAI or compatible embedding models
- **Processing**: Asynchronous batch processing for large document sets
- **Memory Management**: Built-in monitoring and optimization
- **Search Modes**: Hybrid search combines best of semantic and keyword matching
