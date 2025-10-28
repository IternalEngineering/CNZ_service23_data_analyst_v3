# Service23 Consolidation Summary

## What Changed

Service23 has been **consolidated into a single unified API** running on **port 8023**.

Previously, there were plans for two separate services:
- `api_server.py` on port 8023 (slow AI generation endpoints)
- `insights_microservice.py` on port 8024 (fast cached query endpoints)

Now, **everything runs on port 8023** in a single unified `api_server.py`.

---

## Why This Change?

### 1. Simplicity
- **One service** instead of two
- **One port** to remember (8023)
- **One deployment** process
- **One set of logs** to monitor

### 2. Better Developer Experience
- Single API documentation at `http://localhost:8023/docs`
- No confusion about which port to use
- Clearer endpoint organization

### 3. Cleaner Architecture
- Related endpoints grouped together
- Slow (generation) and fast (query) endpoints clearly distinguished
- Consistent response formats

### 4. Easier Deployment
- Deploy one service instead of coordinating two
- Simpler PM2/systemd configuration
- Single health check endpoint

---

## Current Architecture

### Single Service on Port 8023

```
api_server.py (Port 8023)
├── Health & Info
│   ├── GET  /              → API info
│   └── GET  /health        → Detailed health check
│
├── AI Agent (Slow - 2-5 minutes)
│   ├── POST /api/query                      → MindsDB agent
│   └── POST /api/analyze/city-insights      → Generate new insight
│
├── Cached Insights (Fast - < 100ms)
│   ├── POST /chat/city                      → Query city insights
│   ├── POST /chat/cities                    → Query country insights
│   ├── GET  /insights/recent                → Recent insights
│   ├── GET  /insights/{id}                  → Get by UUID
│   └── GET  /insights/city/{name}           → City history
│
└── PostgreSQL Management
    ├── GET  /api/postgres/tables            → List tables
    ├── GET  /api/postgres/schema/{table}    → Get schema
    └── POST /api/postgres/add-column        → Add column
```

---

## File Structure

### Active Files (Port 8023)

```
service23/
├── api_server.py                          ✅ ACTIVE - Unified API server
├── mindsdb_agent.py                       ✅ ACTIVE - MindsDB integration
├── postgres_tool.py                       ✅ ACTIVE - PostgreSQL operations
├── city_insights_analyzer.py              ✅ ACTIVE - AI insight generation
├── CURL_COMMANDS_PORT_8023.md             ✅ NEW - Updated curl commands
└── SERVICE_CONSOLIDATION_SUMMARY.md       ✅ NEW - This file
```

### Reference Files (Port 8024 - For Reference Only)

```
service23/
├── insights_microservice.py               📚 REFERENCE ONLY
├── INSIGHTS_MICROSERVICE_SETUP.md         📚 REFERENCE ONLY
├── test_insights_microservice.py          📚 REFERENCE ONLY
└── test_curl_commands.md                  📚 REFERENCE ONLY (old port 8024)
```

---

## How to Use

### Start the Service

```bash
# Navigate to service23
cd server_c/service23

# Run directly
python api_server.py

# Or with PM2
pm2 start api_server.py --interpreter python --name service23-api
```

### Test the Service

```bash
# Health check
curl http://localhost:8023/health

# Query cached city insights (FAST)
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}'

# Generate new insight (SLOW - 2-5 min)
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{"city": "Bristol", "country_code": "GB"}'
```

### Access Documentation

```bash
# Swagger UI
http://localhost:8023/docs

# ReDoc
http://localhost:8023/redoc
```

---

## Endpoint Categories

### Category 1: Fast Cached Queries (< 100ms)

These endpoints read from the `service23_data_analyst_insights` table and return instantly.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat/city` | POST | Query city insights by name |
| `/chat/cities` | POST | Query insights by country |
| `/insights/recent` | GET | Get recent insights |
| `/insights/{id}` | GET | Get specific insight |
| `/insights/city/{name}` | GET | Get city history |

**Use these for:**
- User-facing queries
- Dashboard displays
- Real-time lookups
- Mobile app queries

### Category 2: Slow AI Generation (2-5 minutes)

These endpoints use AI to generate new insights and store them in the database.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/analyze/city-insights` | POST | Generate new city insight |
| `/api/query` | POST | Query MindsDB agent |

**Use these for:**
- Initial data generation
- Scheduled updates
- Background jobs
- Admin operations

### Category 3: PostgreSQL Management

Direct database operations for admin tasks.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/postgres/tables` | GET | List all tables |
| `/api/postgres/schema/{table}` | GET | Get table schema |
| `/api/postgres/add-column` | POST | Add column to table |

---

## Migration Guide

If you were using the old port 8024 endpoints, here's how to migrate:

### Old (Port 8024)
```bash
curl http://localhost:8024/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}'
```

### New (Port 8023)
```bash
curl http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}'
```

**That's it!** Just change `8024` to `8023` in all your requests.

---

## Workflow Examples

### Example 1: Generate and Query Insights

```bash
# Step 1: Generate new insight (SLOW - run once)
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Bristol",
    "country_code": "GB",
    "success_criteria": "Achieve net zero by 2030"
  }'

# Wait 2-5 minutes for generation to complete...

# Step 2: Query cached insight (FAST - run many times)
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}'
```

### Example 2: Dashboard Display

```bash
# Get recent insights for dashboard
curl http://localhost:8023/insights/recent?limit=10

# Get specific city for detail view
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Manchester"}'
```

### Example 3: Country Overview for Investors

```bash
# Get all UK cities
curl -X POST http://localhost:8023/chat/cities \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me cities in the UK"}'

# Get specific city details
curl http://localhost:8023/insights/city/London?limit=5
```

---

## Response Format

All chat endpoints (`/chat/city`, `/chat/cities`) return consistent format:

```json
{
  "reply": "One-line summary of the insight",
  "replySummary": "Detailed paragraph with context and confidence",
  "table": "service23_data_analyst_insights",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Database Schema

The service reads from and writes to `service23_data_analyst_insights`:

```sql
service23_data_analyst_insights (
    id UUID PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    success_criteria TEXT,
    insight_summary TEXT NOT NULL,
    detailed_analysis TEXT NOT NULL,
    data_sources_used JSONB,
    confidence_score DECIMAL(3,2),
    recommendations JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    alert_sent BOOLEAN,
    alert_id VARCHAR(255)
)
```

---

## Performance Characteristics

| Operation | Endpoint | Response Time | Database Access |
|-----------|----------|---------------|-----------------|
| Query cached insight | `/chat/city` | < 100ms | Read only |
| Get recent insights | `/insights/recent` | < 50ms | Read only |
| Generate new insight | `/api/analyze/city-insights` | 2-5 minutes | Read + Write |
| MindsDB query | `/api/query` | 10-30 seconds | Varies |

---

## Monitoring

### Health Check

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

### Key Metrics to Monitor

1. **Response Time**
   - `/chat/city` should be < 100ms
   - `/api/analyze/city-insights` takes 2-5 minutes (expected)

2. **Database Connection**
   - Check `database: "connected"` in health response
   - Monitor `insights_count` for growth

3. **Error Rates**
   - 404 errors: City not found (expected for new cities)
   - 400 errors: Bad query format
   - 500 errors: Database issues (investigate immediately)

---

## Deployment

### PM2 Configuration

```bash
# Start service
pm2 start api_server.py --interpreter python --name service23-api

# Save configuration
pm2 save

# Setup auto-restart on boot
pm2 startup

# View logs
pm2 logs service23-api

# Monitor
pm2 monit
```

### Systemd Configuration

Create `/etc/systemd/system/service23.service`:

```ini
[Unit]
Description=Service23 Data Analyst Agent API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/urbanzero/server_c/service23
Environment="PATH=/opt/urbanzero/venv/bin"
Environment="PORT=8023"
ExecStart=/opt/urbanzero/venv/bin/python api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable service23
sudo systemctl start service23
sudo systemctl status service23
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check port availability
netstat -ano | findstr :8023  # Windows
lsof -i :8023                 # Linux/Mac

# Check environment variables
python -c "import os; print(os.getenv('DB_HOST'))"

# Test database connection
python -c "import psycopg2; psycopg2.connect('postgresql://...')"
```

### No Insights Found

```bash
# Check database has data
curl http://localhost:8023/insights/recent

# Generate new insights if empty
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{"city": "Bristol", "country_code": "GB"}'
```

### Slow Responses

```bash
# Check database connection
curl http://localhost:8023/health

# Verify using cached endpoints (not generation)
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}'
```

---

## Summary

✅ **One unified service** on port 8023
✅ **Fast cached queries** (< 100ms) for user-facing operations
✅ **Slow AI generation** (2-5 min) for creating new insights
✅ **Clear endpoint organization** with tags and documentation
✅ **Comprehensive curl commands** for testing
✅ **Production-ready** with health checks and monitoring

**All endpoints now accessible at:** `http://localhost:8023`

**Documentation:** `http://localhost:8023/docs`

---

**Service:** Service23 - Data Analyst Agent API
**Version:** 2.0.0
**Port:** 8023
**Status:** Active
**Updated:** 2025-10-28
