# Insights Microservice - cURL Test Commands

Complete collection of cURL commands to test all endpoints.

## Configuration

Default port: **8024** (change if you're using a different port)

```bash
# Set your port
PORT=8024
BASE_URL="http://localhost:${PORT}"
```

---

## 1. Root Health Check

**Endpoint:** `GET /`

```bash
curl http://localhost:8024/
```

**Expected Response:**
```json
{
  "service": "City Insights Microservice",
  "status": "running",
  "version": "1.0.0",
  "port": 8024,
  "docs": "/docs",
  "table": "service23_data_analyst_insights"
}
```

---

## 2. Detailed Health Check

**Endpoint:** `GET /health`

```bash
curl http://localhost:8024/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "city_insights_microservice",
  "database": "connected",
  "insights_count": 15,
  "timestamp": "2025-10-28T12:30:00"
}
```

---

## 3. Query City Insights (Council Officials)

**Endpoint:** `POST /chat/city`

### Example 1: Bristol
```bash
curl -X POST http://localhost:8024/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the insights for Bristol"}'
```

### Example 2: Manchester
```bash
curl -X POST http://localhost:8024/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "What insights do we have for Manchester?"}'
```

### Example 3: London
```bash
curl -X POST http://localhost:8024/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about London"}'
```

### Example 4: Edinburgh
```bash
curl -X POST http://localhost:8024/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Edinburgh data analysis"}'
```

**Expected Response:**
```json
{
  "reply": "Bristol city insights show significant opportunities in renewable energy transition",
  "replySummary": "Analysis for Bristol generated on 2025-10-28 10:30 (Confidence: 85%). The city has strong foundation in sustainability initiatives with multiple renewable energy projects identified. Generated 5 actionable recommendations.",
  "table": "service23_data_analyst_insights",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 4. Query Cities by Country (Investors)

**Endpoint:** `POST /chat/cities`

### Example 1: UK/Great Britain
```bash
curl -X POST http://localhost:8024/chat/cities \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me cities in the UK"}'
```

### Example 2: United Kingdom (alternative)
```bash
curl -X POST http://localhost:8024/chat/cities \
  -H "Content-Type: application/json" \
  -d '{"query": "What cities are available in Great Britain?"}'
```

### Example 3: USA
```bash
curl -X POST http://localhost:8024/chat/cities \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me cities in the USA"}'
```

### Example 4: UAE
```bash
curl -X POST http://localhost:8024/chat/cities \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me cities in the UAE"}'
```

**Expected Response:**
```json
{
  "reply": "London city insights show advanced net-zero readiness",
  "replySummary": "Analysis for London generated on 2025-10-28 12:15 (Confidence: 92%). Comprehensive analysis of London's sustainability landscape reveals strong alignment with net-zero goals. Generated 8 actionable recommendations.",
  "table": "service23_data_analyst_insights",
  "id": "660e8400-e29b-41d4-a716-446655440001"
}
```

---

## 5. Get Recent Insights

**Endpoint:** `GET /insights/recent`

### Get 10 most recent (default)
```bash
curl http://localhost:8024/insights/recent
```

### Get 5 most recent
```bash
curl http://localhost:8024/insights/recent?limit=5
```

### Get 20 most recent
```bash
curl "http://localhost:8024/insights/recent?limit=20"
```

**Expected Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "city": "Bristol",
    "country_code": "GB",
    "insight_summary": "Bristol shows strong renewable energy potential",
    "confidence_score": 0.85,
    "created_at": "2025-10-28T10:30:00"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "city": "Manchester",
    "country_code": "GB",
    "insight_summary": "Manchester demonstrates leadership in urban sustainability",
    "confidence_score": 0.78,
    "created_at": "2025-10-28T09:15:00"
  }
]
```

---

## 6. Get Insight by ID

**Endpoint:** `GET /insights/{insight_id}`

### Example with UUID
```bash
curl http://localhost:8024/insights/550e8400-e29b-41d4-a716-446655440000
```

### With formatted output (jq)
```bash
curl http://localhost:8024/insights/550e8400-e29b-41d4-a716-446655440000 | jq .
```

**Expected Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "city": "Bristol",
  "country_code": "GB",
  "success_criteria": "Achieve net zero by 2030 through renewable energy",
  "insight_summary": "Bristol shows strong renewable energy potential",
  "detailed_analysis": "Comprehensive analysis reveals Bristol has made significant progress toward net-zero goals. The city has invested in solar panel infrastructure, implemented energy efficiency programs, and fostered partnerships with renewable energy providers...",
  "data_sources_used": ["opportunities", "data_sources", "reports"],
  "confidence_score": 0.85,
  "recommendations": [
    {
      "priority": "high",
      "action": "Implement solar panel program for municipal buildings",
      "expected_impact": "20% emissions reduction",
      "timeline": "12-18 months"
    },
    {
      "priority": "medium",
      "action": "Expand electric vehicle charging infrastructure",
      "expected_impact": "15% reduction in transport emissions",
      "timeline": "18-24 months"
    }
  ],
  "created_at": "2025-10-28T10:30:00",
  "updated_at": "2025-10-28T10:30:00",
  "alert_sent": true,
  "alert_id": "alert_123"
}
```

---

## 7. Get All Insights for a City

**Endpoint:** `GET /insights/city/{city_name}`

### Bristol (default GB)
```bash
curl http://localhost:8024/insights/city/Bristol
```

### Bristol with explicit country code
```bash
curl "http://localhost:8024/insights/city/Bristol?country_code=GB"
```

### Bristol with limit
```bash
curl "http://localhost:8024/insights/city/Bristol?country_code=GB&limit=5"
```

### Manchester
```bash
curl "http://localhost:8024/insights/city/Manchester?country_code=GB&limit=10"
```

### London
```bash
curl http://localhost:8024/insights/city/London
```

**Expected Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "city": "Bristol",
    "country_code": "GB",
    "insight_summary": "Recent analysis shows progress in renewable adoption",
    "confidence_score": 0.85,
    "created_at": "2025-10-28T10:30:00"
  },
  {
    "id": "440e8400-e29b-41d4-a716-446655440099",
    "city": "Bristol",
    "country_code": "GB",
    "insight_summary": "Historical data indicates strong sustainability foundation",
    "confidence_score": 0.82,
    "created_at": "2025-10-20T14:20:00"
  }
]
```

---

## Interactive API Documentation

Access the interactive Swagger UI to test all endpoints in your browser:

```bash
# Open in browser
start http://localhost:8024/docs

# Or on Linux/Mac
open http://localhost:8024/docs
```

Alternative documentation (ReDoc):
```bash
start http://localhost:8024/redoc
```

---

## Error Handling Examples

### 404 - City Not Found
```bash
curl -X POST http://localhost:8024/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me NonExistentCity"}'
```

**Response:**
```json
{
  "detail": "No insights found for NonExistentCity, GB"
}
```

### 400 - Bad Request (no city in query)
```bash
curl -X POST http://localhost:8024/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me something"}'
```

**Response:**
```json
{
  "detail": "Could not identify a city in your query. Please mention a specific city name."
}
```

### 404 - Insight ID Not Found
```bash
curl http://localhost:8024/insights/00000000-0000-0000-0000-000000000000
```

**Response:**
```json
{
  "detail": "Insight with ID 00000000-0000-0000-0000-000000000000 not found"
}
```

---

## Batch Testing Script

Save this as `test_all_endpoints.sh`:

```bash
#!/bin/bash

PORT=8024
BASE_URL="http://localhost:${PORT}"

echo "================================="
echo "Testing Insights Microservice"
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

echo -e "\n6. Get city insights (Bristol)..."
curl -s "${BASE_URL}/insights/city/Bristol?limit=3" | jq .

echo -e "\n================================="
echo "All tests completed!"
echo "================================="
```

Run with:
```bash
chmod +x test_all_endpoints.sh
./test_all_endpoints.sh
```

---

## Windows PowerShell Version

Save as `test_all_endpoints.ps1`:

```powershell
$PORT = 8024
$BASE_URL = "http://localhost:$PORT"

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Testing Insights Microservice" -ForegroundColor Cyan
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

Write-Host "`n5. Get recent insights..." -ForegroundColor Yellow
curl.exe -s "$BASE_URL/insights/recent?limit=5" | ConvertFrom-Json | ConvertTo-Json

Write-Host "`n=================================" -ForegroundColor Cyan
Write-Host "All tests completed!" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
```

Run with:
```powershell
.\test_all_endpoints.ps1
```

---

## Quick Reference Table

| Method | Endpoint | Purpose | Example |
|--------|----------|---------|---------|
| GET | `/` | Root health check | `curl http://localhost:8024/` |
| GET | `/health` | Detailed health | `curl http://localhost:8024/health` |
| POST | `/chat/city` | City insights | `curl -X POST ... -d '{"query":"Bristol"}'` |
| POST | `/chat/cities` | Country insights | `curl -X POST ... -d '{"query":"UK"}'` |
| GET | `/insights/recent` | Recent insights | `curl http://localhost:8024/insights/recent` |
| GET | `/insights/{id}` | Get by ID | `curl http://localhost:8024/insights/{uuid}` |
| GET | `/insights/city/{name}` | City history | `curl http://localhost:8024/insights/city/Bristol` |

---

## Tips

1. **Pretty Print with jq**: Add `| jq .` to any curl command
2. **Save Response**: Add `-o output.json` to save response
3. **Verbose Mode**: Add `-v` to see full HTTP request/response
4. **Silent Mode**: Add `-s` to suppress progress bar
5. **Follow Redirects**: Add `-L` if needed

```bash
# Example: Pretty print and save
curl -s http://localhost:8024/insights/recent | jq . | tee recent_insights.json

# Example: Verbose request
curl -v -X POST http://localhost:8024/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Bristol"}'
```

---

## Environment Variables

If running on a different port:

```bash
# Bash/Linux/Mac
export PORT=8025
curl http://localhost:$PORT/

# Windows CMD
set PORT=8025
curl http://localhost:%PORT%/

# Windows PowerShell
$env:PORT=8025
curl http://localhost:$env:PORT/
```
