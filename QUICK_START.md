# Service23 - Quick Start Guide

## TL;DR

**Everything runs on port 8023 now.**

```bash
# Start the service
python api_server.py

# Test it
curl http://localhost:8023/health

# View docs
start http://localhost:8023/docs
```

---

## Essential Commands

### Start Service
```bash
python api_server.py
```

### Health Check
```bash
curl http://localhost:8023/health
```

### Query Cached City Insights (FAST)
```bash
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}'
```

### Query Country Insights (FAST)
```bash
curl -X POST http://localhost:8023/chat/cities \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me UK cities"}'
```

### Generate New Insight (SLOW - 2-5 min)
```bash
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{"city": "Bristol", "country_code": "GB"}'
```

---

## Key Files

| File | Purpose |
|------|---------|
| `api_server.py` | **Main service** - All endpoints on port 8023 |
| `CURL_COMMANDS_PORT_8023.md` | **Complete curl examples** |
| `SERVICE_CONSOLIDATION_SUMMARY.md` | **Architecture overview** |
| `QUICK_START.md` | **This file** - Quick reference |

---

## All Endpoints

### Fast (< 100ms) - Use These
- `POST /chat/city` - Query city insights
- `POST /chat/cities` - Query country insights
- `GET /insights/recent` - Recent insights
- `GET /insights/{id}` - Get by UUID
- `GET /insights/city/{name}` - City history

### Slow (2-5 min) - Use Sparingly
- `POST /api/analyze/city-insights` - Generate new insight
- `POST /api/query` - MindsDB agent query

---

## Common Tasks

### View All Endpoints
```bash
curl http://localhost:8023/ | jq .
```

### Get Recent Insights
```bash
curl http://localhost:8023/insights/recent?limit=10
```

### Query Specific City
```bash
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Manchester"}'
```

### Generate Insight for New City
```bash
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Edinburgh",
    "country_code": "GB",
    "success_criteria": "Achieve net zero by 2030"
  }'
```

---

## Documentation

**Interactive API docs:** http://localhost:8023/docs

**Alternative docs:** http://localhost:8023/redoc

---

## Port Information

| Service | Port | Status |
|---------|------|--------|
| Service23 API | **8023** | ✅ Active (unified service) |
| Old Microservice | ~~8024~~ | ❌ Deprecated (merged into 8023) |

---

## What Changed?

Previously planned: Two separate services (8023 + 8024)
Now: **One unified service on port 8023**

All features from both services are now available at port 8023.

---

## Need More Info?

- **Complete curl commands:** `CURL_COMMANDS_PORT_8023.md`
- **Architecture details:** `SERVICE_CONSOLIDATION_SUMMARY.md`
- **Interactive testing:** http://localhost:8023/docs

---

**Service:** Service23 - Data Analyst Agent API
**Port:** 8023
**Version:** 2.0.0
**Status:** ✅ Ready
