# Service23 Documentation

Welcome to the Service23 - Data Analyst Agent API documentation.

## 📚 Documentation Index

### Main Documentation

- **[API.md](./API.md)** - Complete API reference with all endpoints, examples, and technical details

### Quick References

- **[Quick Start Guide](../QUICK_START.md)** - Get started in 2 minutes
- **[cURL Commands](../CURL_COMMANDS_PORT_8023.md)** - All curl examples for testing
- **[Consolidation Summary](../SERVICE_CONSOLIDATION_SUMMARY.md)** - Architecture overview and migration guide

## 🚀 Quick Start

```bash
# 1. Start the service
python api_server.py

# 2. Check health
curl http://localhost:8023/health

# 3. Query cached insights (fast)
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}'

# 4. View interactive docs
start http://localhost:8023/docs
```

## 📖 What's Inside

### [API.md](./API.md)

**Complete technical reference** covering:

1. **Architecture Overview** - System design and components
2. **All Endpoints** - Detailed documentation for every endpoint
3. **Data Models** - Request/response schemas
4. **Error Handling** - Error codes and troubleshooting
5. **Natural Language Parsing** - How query parsing works
6. **Database Schema** - Complete database structure
7. **Examples & Use Cases** - Real-world usage scenarios
8. **Performance** - Response times and optimization
9. **Deployment** - Production deployment guide

## 🔗 Interactive Documentation

- **Swagger UI:** http://localhost:8023/docs
- **ReDoc:** http://localhost:8023/redoc

## 📊 Endpoint Categories

### Fast Endpoints (< 100ms)
Query pre-generated insights from cache

- `POST /chat/city` - City-specific insights
- `POST /chat/cities` - Country-level insights
- `GET /insights/recent` - Recent insights
- `GET /insights/{id}` - Get by UUID
- `GET /insights/city/{name}` - City history

### Slow Endpoints (2-5 minutes)
Generate new insights with AI

- `POST /api/analyze/city-insights` - Generate city insight
- `POST /api/query` - MindsDB agent query

### Management Endpoints
Database operations

- `GET /api/postgres/tables` - List tables
- `GET /api/postgres/schema/{table}` - Get schema
- `POST /api/postgres/add-column` - Add column

## 🎯 Common Use Cases

### Dashboard Display
```bash
curl http://localhost:8023/insights/recent?limit=10
```

### City Detail View
```bash
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Manchester"}'
```

### Generate New Insight
```bash
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Edinburgh",
    "country_code": "GB",
    "success_criteria": "Achieve net zero by 2030"
  }'
```

## 🔍 Search the Documentation

Looking for something specific? Here are common topics:

- **Endpoints:** See [API.md - Endpoint Categories](./API.md#endpoint-categories)
- **Error Codes:** See [API.md - Error Handling](./API.md#error-handling)
- **Data Models:** See [API.md - Data Models](./API.md#data-models)
- **Performance:** See [API.md - Performance](./API.md#performance-characteristics)
- **Examples:** See [API.md - Examples](./API.md#examples--use-cases)
- **Deployment:** See [API.md - Deployment](./API.md#deployment)

## 📝 Quick Examples

### Health Check
```bash
curl http://localhost:8023/health
```

### Query City Insights
```bash
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}'
```

### Get Recent Insights
```bash
curl http://localhost:8023/insights/recent?limit=5
```

## 🛠️ API Information

- **Base URL:** `http://localhost:8023`
- **Version:** 2.0.0
- **Port:** 8023
- **Status:** ✅ Production Ready

## 📈 Response Times

| Endpoint Type | Response Time |
|--------------|---------------|
| Health checks | 10-50ms |
| Cached insights | 50-100ms |
| Recent insights | 20-50ms |
| AI generation | 2-5 minutes |

## 🔐 Authentication

**Current Status:** Open (no auth required)

**Future:** JWT tokens + API keys (coming soon)

## 💡 Tips

1. **Always use cached endpoints** for user-facing queries
2. **Limit slow endpoint usage** to background jobs
3. **Cache responses** client-side for 5-10 minutes
4. **Use UUIDs directly** when available
5. **Monitor health endpoint** for service status

## 📞 Need Help?

1. **Check the main API docs:** [API.md](./API.md)
2. **Try interactive docs:** http://localhost:8023/docs
3. **Review examples:** [CURL_COMMANDS_PORT_8023.md](../CURL_COMMANDS_PORT_8023.md)
4. **Read consolidation guide:** [SERVICE_CONSOLIDATION_SUMMARY.md](../SERVICE_CONSOLIDATION_SUMMARY.md)

## 🗂️ File Structure

```
service23/
├── docs/
│   ├── README.md              (This file)
│   └── API.md                 (Complete API reference)
├── api_server.py              (Main service)
├── QUICK_START.md             (Quick reference)
├── CURL_COMMANDS_PORT_8023.md (cURL examples)
└── SERVICE_CONSOLIDATION_SUMMARY.md (Architecture)
```

## 🎓 Learning Path

**New to the API?**

1. Start with **[QUICK_START.md](../QUICK_START.md)** (2 minutes)
2. Try examples from **[CURL_COMMANDS_PORT_8023.md](../CURL_COMMANDS_PORT_8023.md)**
3. Explore **[Swagger UI](http://localhost:8023/docs)** interactively
4. Deep dive into **[API.md](./API.md)** for complete reference
5. Understand architecture with **[SERVICE_CONSOLIDATION_SUMMARY.md](../SERVICE_CONSOLIDATION_SUMMARY.md)**

**Building an integration?**

1. Review **[API.md - Data Models](./API.md#data-models)**
2. Study **[API.md - Examples](./API.md#examples--use-cases)**
3. Check **[API.md - Error Handling](./API.md#error-handling)**
4. Review **[Performance Characteristics](./API.md#performance-characteristics)**

**Deploying to production?**

1. Read **[API.md - Deployment](./API.md#deployment)**
2. Review **[API.md - Monitoring](./API.md#deployment)**
3. Check **[SERVICE_CONSOLIDATION_SUMMARY.md - Deployment](../SERVICE_CONSOLIDATION_SUMMARY.md#deployment)**

---

**Service:** Service23 - Data Analyst Agent API
**Documentation Version:** 2.0.0
**Last Updated:** 2025-10-28
