# Service23 API - cURL Commands (Port 8023)

Complete collection of cURL commands for all Service23 endpoints running on **port 8023**.

## Base Configuration

```bash
PORT=8023
BASE_URL="http://localhost:${PORT}"
```

---

## Health & Info Endpoints

### 1. Root API Info
```bash
curl http://localhost:8023/
```

**Response:**
```json
{
  "name": "Service23 - Data Analyst Agent API",
  "version": "2.0.0",
  "status": "running",
  "port": 8023,
  "endpoints": {
    "health": "/health (GET)",
    "docs": "/docs (Swagger UI)",
    "agent_query": "/api/query (POST)",
    "generate_insight": "/api/analyze/city-insights (POST) - slow",
    "query_city": "/chat/city (POST) - fast",
    "query_country": "/chat/cities (POST) - fast",
    ...
  }
}
```

### 2. Health Check
```bash
curl http://localhost:8023/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "service23_data_analyst_agent",
  "database": "connected",
  "insights_count": 15,
  "timestamp": "2025-10-28T12:30:00"
}
```

---

## AI Agent Endpoints (Slow - Generates New Data)

### 3. Query MindsDB Agent
```bash
curl -X POST http://localhost:8023/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many records are in service19_onboarding_data?"}'
```

### 4. Generate New City Insight (2-5 minutes)
```bash
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Bristol",
    "country_code": "GB",
    "success_criteria": "Achieve net zero by 2030"
  }'
```

---

## Cached Insights Endpoints (Fast - Reads from Database)

### 5. Query City Insights
```bash
# Bristol
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the insights for Bristol"}'

# Manchester
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "What insights do we have for Manchester?"}'

# London
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about London"}'
```

**Response:**
```json
{
  "reply": "Bristol city insights show significant opportunities",
  "replySummary": "Analysis for Bristol generated on 2025-10-28...",
  "table": "service23_data_analyst_insights",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 6. Query Cities by Country
```bash
# UK cities
curl -X POST http://localhost:8023/chat/cities \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me cities in the UK"}'

# USA cities
curl -X POST http://localhost:8023/chat/cities \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me cities in the USA"}'
```

### 7. Get Recent Insights
```bash
# Default (10 results)
curl http://localhost:8023/insights/recent

# Custom limit
curl http://localhost:8023/insights/recent?limit=5
curl "http://localhost:8023/insights/recent?limit=20"
```

### 8. Get Insight by ID
```bash
curl http://localhost:8023/insights/550e8400-e29b-41d4-a716-446655440000

# With jq for pretty print
curl http://localhost:8023/insights/550e8400-e29b-41d4-a716-446655440000 | jq .
```

### 9. Get City Insight History
```bash
# Bristol
curl http://localhost:8023/insights/city/Bristol

# With parameters
curl "http://localhost:8023/insights/city/Bristol?country_code=GB&limit=5"

# Manchester
curl "http://localhost:8023/insights/city/Manchester?country_code=GB&limit=10"
```

---

## PostgreSQL Management Endpoints

### 10. List All Tables
```bash
curl http://localhost:8023/api/postgres/tables
```

### 11. Get Table Schema
```bash
curl http://localhost:8023/api/postgres/schema/service23_data_analyst_insights
```

### 12. Add Column to Table
```bash
curl -X POST http://localhost:8023/api/postgres/add-column \
  -H "Content-Type: application/json" \
  -d '{
    "table": "service19_onboarding_data",
    "column_name": "new_column",
    "column_type": "VARCHAR(255)",
    "default_value": "default_value"
  }'
```

---

## Interactive Documentation

```bash
# Swagger UI (recommended)
start http://localhost:8023/docs

# ReDoc (alternative)
start http://localhost:8023/redoc

# Linux/Mac
open http://localhost:8023/docs
open http://localhost:8023/redoc
```

---

## Complete Testing Script (Bash)

```bash
#!/bin/bash

PORT=8023
BASE_URL="http://localhost:${PORT}"

echo "================================="
echo "Testing Service23 API (Port 8023)"
echo "================================="

echo -e "\n1. Root health check..."
curl -s "${BASE_URL}/" | jq .

echo -e "\n2. Detailed health check..."
curl -s "${BASE_URL}/health" | jq .

echo -e "\n3. Query city insights (Bristol)..."
curl -s -X POST "${BASE_URL}/chat/city" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}' | jq .

echo -e "\n4. Query cities by country (UK)..."
curl -s -X POST "${BASE_URL}/chat/cities" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me UK cities"}' | jq .

echo -e "\n5. Get recent insights..."
curl -s "${BASE_URL}/insights/recent?limit=5" | jq .

echo -e "\n================================="
echo "All tests completed!"
echo "================================="
```

---

## Windows PowerShell Script

```powershell
$PORT = 8023
$BASE_URL = "http://localhost:$PORT"

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Testing Service23 API (Port 8023)" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

Write-Host "`n1. Root health check..." -ForegroundColor Yellow
curl.exe -s "$BASE_URL/" | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n2. Detailed health check..." -ForegroundColor Yellow
curl.exe -s "$BASE_URL/health" | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n3. Query city insights (Bristol)..." -ForegroundColor Yellow
curl.exe -s -X POST "$BASE_URL/chat/city" `
  -H "Content-Type: application/json" `
  -d '{"query": "Show me Bristol"}' | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n4. Query cities by country (UK)..." -ForegroundColor Yellow
curl.exe -s -X POST "$BASE_URL/chat/cities" `
  -H "Content-Type: application/json" `
  -d '{"query": "Show me UK cities"}' | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n=================================" -ForegroundColor Cyan
Write-Host "All tests completed!" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
```

---

## Quick Reference Table

| Method | Endpoint | Speed | Purpose |
|--------|----------|-------|---------|
| GET | `/` | Instant | API info |
| GET | `/health` | Instant | Health check |
| POST | `/chat/city` | **Fast** | Cached city insights |
| POST | `/chat/cities` | **Fast** | Cached country insights |
| GET | `/insights/recent` | **Fast** | Recent insights list |
| GET | `/insights/{id}` | **Fast** | Get by UUID |
| GET | `/insights/city/{name}` | **Fast** | City history |
| POST | `/api/analyze/city-insights` | **Slow (2-5 min)** | Generate new insight |
| POST | `/api/query` | Medium | MindsDB agent query |

---

## Key Differences: Fast vs Slow Endpoints

### Fast Endpoints (< 100ms)
- `/chat/city` - Query cached city insights
- `/chat/cities` - Query cached country insights
- `/insights/*` - All insights query endpoints
- **Use these for:** Quick lookups, dashboards, user-facing queries

### Slow Endpoints (2-5 minutes)
- `/api/analyze/city-insights` - Generate new insight with AI
- **Use this for:** Creating new analysis, initial data generation

---

## Error Handling Examples

### 404 - City Not Found
```bash
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me NonExistentCity"}'
```

**Response:**
```json
{
  "detail": "No insights found for NonExistentCity, GB"
}
```

### 400 - Bad Request
```bash
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me something"}'
```

**Response:**
```json
{
  "detail": "Could not identify a city in your query. Please mention a specific city name."
}
```

---

## Tips & Tricks

### Pretty Print with jq
```bash
curl http://localhost:8023/insights/recent | jq .
```

### Save Response to File
```bash
curl http://localhost:8023/insights/recent > insights.json
```

### Verbose Mode (see full HTTP)
```bash
curl -v http://localhost:8023/health
```

### Follow Redirects
```bash
curl -L http://localhost:8023/some-endpoint
```

### Time the Request
```bash
time curl http://localhost:8023/insights/recent
```

### Silent Mode (no progress bar)
```bash
curl -s http://localhost:8023/health
```

---

## Environment Variables

```bash
# Bash
export PORT=8023
curl http://localhost:$PORT/

# Windows CMD
set PORT=8023
curl http://localhost:%PORT%/

# PowerShell
$env:PORT=8023
curl http://localhost:$env:PORT/
```

---

## Complete Endpoint List

### Health & Info
- `GET /` - API info
- `GET /health` - Health check with DB status

### AI Agent (Slow)
- `POST /api/query` - Query MindsDB agent
- `POST /api/analyze/city-insights` - Generate new insight

### Cached Insights (Fast)
- `POST /chat/city` - Query city insights
- `POST /chat/cities` - Query country insights
- `GET /insights/recent` - Recent insights
- `GET /insights/{id}` - Get by UUID
- `GET /insights/city/{name}` - City history

### PostgreSQL
- `GET /api/postgres/tables` - List tables
- `GET /api/postgres/schema/{table}` - Get schema
- `POST /api/postgres/add-column` - Add column

### Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

---

**Port:** 8023
**Service:** Service23 - Data Analyst Agent API
**Version:** 2.0.0
**Updated:** 2025-10-28
