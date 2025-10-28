# Service23 - Data Analyst Agent API Documentation

## Overview

Service23 is a comprehensive FastAPI-based service that provides intelligent city insights analysis through AI-powered agents combined with real-time cached data access. The service operates on **port 8023** and offers both slow AI generation endpoints and fast cached query endpoints in a unified API.

**Base URL:** `http://localhost:8023`

**Version:** 2.0.0

**Interactive Documentation:**
- Swagger UI: http://localhost:8023/docs
- ReDoc: http://localhost:8023/redoc

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Authentication](#authentication)
3. [Endpoint Categories](#endpoint-categories)
4. [Health & Information Endpoints](#health--information-endpoints)
5. [Cached Insights Endpoints (Fast)](#cached-insights-endpoints-fast)
6. [AI Generation Endpoints (Slow)](#ai-generation-endpoints-slow)
7. [PostgreSQL Management Endpoints](#postgresql-management-endpoints)
8. [Data Models](#data-models)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)
11. [Natural Language Query Parsing](#natural-language-query-parsing)
12. [Database Schema](#database-schema)
13. [Examples & Use Cases](#examples--use-cases)
14. [Performance Characteristics](#performance-characteristics)
15. [Deployment](#deployment)

---

## Architecture Overview

### Service Components

```
┌─────────────────────────────────────────────────────────┐
│         Service23 - Data Analyst Agent API              │
│                    (Port 8023)                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────┐    ┌──────────────────────┐   │
│  │  Fast Endpoints    │    │  Slow Endpoints      │   │
│  │  (< 100ms)         │    │  (2-5 minutes)       │   │
│  ├────────────────────┤    ├──────────────────────┤   │
│  │ • /chat/city       │    │ • /api/analyze/*     │   │
│  │ • /chat/cities     │    │ • /api/query         │   │
│  │ • /insights/*      │    │                      │   │
│  └────────┬───────────┘    └──────────┬───────────┘   │
│           │                           │               │
│           ▼                           ▼               │
│  ┌────────────────────┐    ┌──────────────────────┐   │
│  │   PostgreSQL DB    │    │   AI Agents          │   │
│  │   (Read Cache)     │    │   • MindsDB          │   │
│  │                    │    │   • OpenAI           │   │
│  └────────────────────┘    │   • City Analyzer    │   │
│                             └──────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Request Flow

#### Fast Path (Cached Queries)
```
User Request → API Endpoint → PostgreSQL Cache → Response
             (< 100ms)
```

#### Slow Path (AI Generation)
```
User Request → API Endpoint → AI Agent → Multiple Data Sources
                                         ↓
                                   Analyze & Generate
                                         ↓
                               Store in PostgreSQL → Response
             (2-5 minutes)
```

### Technology Stack

- **Framework:** FastAPI 0.109+
- **Server:** Uvicorn
- **Database:** PostgreSQL 16.3 (AWS RDS)
- **AI/ML:**
  - OpenAI GPT-4o (via OpenRouter/LiteLLM)
  - Anthropic Claude (via Claude SDK)
  - MindsDB for data queries
- **Telemetry:** Arize Phoenix
- **Authentication:** AWS Cognito (optional)

---

## Authentication

### Current Status
The API currently operates in **open mode** without authentication requirements. All endpoints are publicly accessible.

### Future Implementation
Authentication will be implemented using:
- **JWT tokens** from AWS Cognito
- **API keys** for service-to-service communication
- **Role-based access control** (RBAC) for admin endpoints

**Recommended Headers (when auth is enabled):**
```http
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
```

---

## Endpoint Categories

The API is organized into four main categories:

### 1. Health & Information (Instant)
Status checks and API information
- `GET /` - API information
- `GET /health` - Detailed health check

### 2. Cached Insights (Fast - < 100ms)
Real-time access to pre-generated insights
- `POST /chat/city` - Query city insights
- `POST /chat/cities` - Query country insights
- `GET /insights/recent` - Recent insights
- `GET /insights/{id}` - Get by UUID
- `GET /insights/city/{name}` - City history

### 3. AI Generation (Slow - 2-5 minutes)
Generate new insights using AI
- `POST /api/analyze/city-insights` - Generate city insight
- `POST /api/query` - MindsDB agent query

### 4. PostgreSQL Management
Database operations for admins
- `GET /api/postgres/tables` - List tables
- `GET /api/postgres/schema/{table}` - Get schema
- `POST /api/postgres/add-column` - Add column

---

## Health & Information Endpoints

### GET /

**Description:** Get API information and available endpoints

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
    "redoc": "/redoc (ReDoc)",
    "agent_query": "/api/query (POST)",
    "generate_insight": "/api/analyze/city-insights (POST)",
    "query_city": "/chat/city (POST)",
    "query_country": "/chat/cities (POST)",
    "recent_insights": "/insights/recent (GET)",
    "insight_by_id": "/insights/{id} (GET)",
    "city_history": "/insights/city/{name} (GET)"
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8023/
```

---

### GET /health

**Description:** Comprehensive health check with database connectivity status

**Response:**
```json
{
  "status": "healthy",
  "service": "service23_data_analyst_agent",
  "database": "connected",
  "insights_count": 42,
  "timestamp": "2025-10-28T15:30:00.123456"
}
```

**Response Fields:**
- `status` - Overall service status (`healthy` | `unhealthy`)
- `service` - Service identifier
- `database` - Database connection status (`connected` | `disconnected`)
- `insights_count` - Total number of insights in database
- `timestamp` - Current server timestamp (ISO 8601)

**cURL Example:**
```bash
curl http://localhost:8023/health
```

**Error Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "service": "service23_data_analyst_agent",
  "database": "disconnected",
  "error": "connection refused: host unreachable",
  "timestamp": "2025-10-28T15:30:00.123456"
}
```

---

## Cached Insights Endpoints (Fast)

These endpoints provide instant access to pre-generated insights stored in the database. Response time is typically **< 100ms**.

### POST /chat/city

**Description:** Natural language query for specific city insights (for council officials)

**Use Case:** Council officials checking their city's insights

**Request Body:**
```json
{
  "query": "Show me the insights for Bristol"
}
```

**Supported Query Formats:**
- "Show me the insights for Bristol"
- "What insights do we have for Manchester?"
- "Tell me about Edinburgh's data analysis"
- "London insights"
- "What about Glasgow?"

**Response:**
```json
{
  "reply": "Bristol shows strong renewable energy potential with high sustainability readiness",
  "replySummary": "Analysis for Bristol generated on 2025-10-28 14:30 (Confidence: 85%). The city has established strong foundation in sustainability initiatives with multiple renewable energy projects identified across residential and commercial sectors. Data analysis reveals significant opportunities in solar panel deployment and energy efficiency programs. Generated 5 actionable recommendations.",
  "table": "service23_data_analyst_insights",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response Fields:**
- `reply` - One-line summary of the insight
- `replySummary` - Detailed paragraph with context and confidence score
- `table` - Source database table
- `id` - UUID of the insight record

**Error Responses:**

**400 - City Not Identified:**
```json
{
  "detail": "Could not identify a city in your query. Please mention a specific city name."
}
```

**404 - No Insights Found:**
```json
{
  "detail": "No insights found for CityName, GB"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the insights for Bristol"
  }'
```

**Performance:** < 100ms

---

### POST /chat/cities

**Description:** Natural language query for city insights by country (for investors)

**Use Case:** Investors exploring opportunities across multiple cities

**Request Body:**
```json
{
  "query": "Show me cities in the UK"
}
```

**Supported Query Formats:**
- "Show me cities in the UK"
- "What cities are available in Great Britain?"
- "List all UK city insights"
- "Show me USA cities"
- "Cities in the United States"

**Supported Countries:**
- UK/Britain/England/Scotland/Wales → GB
- USA/America/United States → US
- UAE/Dubai/Emirates → AE
- Singapore → SG
- Japan → JP

**Response:**
```json
{
  "reply": "London demonstrates advanced net-zero readiness with comprehensive sustainability framework",
  "replySummary": "Analysis for London generated on 2025-10-28 12:15 (Confidence: 92%). Comprehensive analysis of London's sustainability landscape reveals strong alignment with net-zero goals including advanced transportation electrification, building efficiency programs, and renewable energy integration. The city benefits from established policy frameworks and significant private investment in green technologies. Generated 8 actionable recommendations.",
  "table": "service23_data_analyst_insights",
  "id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Note:** Returns the most recent insight for the specified country.

**Error Response:**

**404 - No Insights for Country:**
```json
{
  "detail": "No insights found for country: GB"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8023/chat/cities \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me cities in the UK"
  }'
```

**Performance:** < 100ms

---

### GET /insights/recent

**Description:** Get recent insights across all cities

**Use Case:** Dashboard displays, overview pages, recent activity monitoring

**Query Parameters:**
- `limit` (optional, default: 10) - Number of insights to return (1-100)

**Response:**
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

**Response Fields:**
- `id` - Unique UUID identifier
- `city` - City name
- `country_code` - ISO 3166-1 alpha-2 country code
- `insight_summary` - Brief summary of the insight
- `confidence_score` - AI confidence score (0.0 to 1.0)
- `created_at` - Timestamp when insight was generated

**cURL Examples:**
```bash
# Default (10 results)
curl http://localhost:8023/insights/recent

# Custom limit
curl http://localhost:8023/insights/recent?limit=5
curl "http://localhost:8023/insights/recent?limit=20"
```

**Performance:** < 50ms

---

### GET /insights/{insight_id}

**Description:** Get complete details for a specific insight by UUID

**Use Case:** Detailed insight view, full analysis retrieval

**Path Parameters:**
- `insight_id` (required) - UUID of the insight

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "city": "Bristol",
  "country_code": "GB",
  "success_criteria": "Achieve net zero by 2030 through renewable energy transition",
  "insight_summary": "Bristol shows strong renewable energy potential",
  "detailed_analysis": "Comprehensive analysis reveals Bristol has made significant progress toward net-zero goals. The city has invested in solar panel infrastructure across 23% of municipal buildings, implemented energy efficiency programs reaching 15,000 residential properties, and fostered partnerships with three major renewable energy providers. Current emissions data shows a 34% reduction from 2015 baseline levels, positioning Bristol ahead of the national average. Key opportunities exist in expanding residential solar adoption, implementing district heating systems, and accelerating commercial building retrofits...",
  "data_sources_used": [
    "opportunities",
    "data_sources",
    "reports",
    "service6_onboarding_voice"
  ],
  "confidence_score": 0.85,
  "recommendations": [
    {
      "priority": "high",
      "category": "renewable_energy",
      "action": "Implement municipal solar panel program for public buildings",
      "expected_impact": "20% reduction in municipal energy costs, 15% emissions reduction",
      "timeline": "12-18 months",
      "estimated_cost": "£2.5M - £3.2M",
      "roi_years": 7.5
    },
    {
      "priority": "high",
      "category": "transportation",
      "action": "Expand electric vehicle charging infrastructure",
      "expected_impact": "15% reduction in transport emissions",
      "timeline": "18-24 months",
      "estimated_cost": "£1.8M - £2.3M",
      "roi_years": 9.2
    }
  ],
  "created_at": "2025-10-28T10:30:00",
  "updated_at": "2025-10-28T10:30:00",
  "alert_sent": true,
  "alert_id": "alert_bristol_2025_10_28"
}
```

**Response Fields:**
- `id` - Unique UUID identifier
- `city` - City name
- `country_code` - ISO country code
- `success_criteria` - Success criteria used for analysis
- `insight_summary` - Brief summary
- `detailed_analysis` - Complete analysis text
- `data_sources_used` - Array of data source table names
- `confidence_score` - AI confidence (0.0 to 1.0)
- `recommendations` - Array of actionable recommendations with details
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `alert_sent` - Whether alert was sent to platform
- `alert_id` - Reference to created alert

**Error Response:**

**404 - Insight Not Found:**
```json
{
  "detail": "Insight with ID 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

**cURL Example:**
```bash
curl http://localhost:8023/insights/550e8400-e29b-41d4-a716-446655440000

# With jq for pretty formatting
curl http://localhost:8023/insights/550e8400-e29b-41d4-a716-446655440000 | jq .
```

**Performance:** < 100ms

---

### GET /insights/city/{city_name}

**Description:** Get all insights for a specific city (historical view)

**Use Case:** Tracking city progress over time, historical analysis

**Path Parameters:**
- `city_name` (required) - Name of the city (case-insensitive)

**Query Parameters:**
- `country_code` (optional, default: "GB") - ISO country code
- `limit` (optional, default: 10) - Number of insights to return

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "city": "Bristol",
    "country_code": "GB",
    "insight_summary": "Recent analysis shows progress in renewable energy adoption",
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

**Error Response:**

**404 - No Insights Found:**
```json
{
  "detail": "No insights found for Bristol, GB"
}
```

**cURL Examples:**
```bash
# Default (GB)
curl http://localhost:8023/insights/city/Bristol

# With country code
curl "http://localhost:8023/insights/city/Bristol?country_code=GB"

# With limit
curl "http://localhost:8023/insights/city/Bristol?country_code=GB&limit=5"

# Manchester
curl "http://localhost:8023/insights/city/Manchester?limit=10"
```

**Performance:** < 100ms

---

## AI Generation Endpoints (Slow)

These endpoints use AI agents to generate new insights. They are computationally expensive and typically take **2-5 minutes** to complete.

### POST /api/analyze/city-insights

**Description:** Generate comprehensive city insights using AI agent analysis

**Use Case:** Initial data generation, periodic updates, new city onboarding

**Request Body:**
```json
{
  "city": "Bristol",
  "country_code": "GB",
  "success_criteria": "Achieve net zero by 2030 through renewable energy transition"
}
```

**Request Fields:**
- `city` (required) - City name
- `country_code` (required) - ISO 3166-1 alpha-2 country code
- `success_criteria` (optional) - Success criteria for analysis

**Processing Steps:**
1. Query service6_onboarding_voice for success criteria (if not provided)
2. Gather data from multiple sources:
   - opportunities table
   - data_sources table
   - reports table
   - external data sources
3. Use AI agent to analyze and connect information
4. Generate actionable recommendations
5. Calculate confidence score
6. Store results in service23_data_analyst_insights table
7. Create alert on web platform (if configured)

**Response:**
```json
{
  "success": true,
  "insight_id": "550e8400-e29b-41d4-a716-446655440000",
  "city": "Bristol",
  "country_code": "GB",
  "insight": {
    "summary": "Bristol shows strong renewable energy potential",
    "detailed_analysis": "...",
    "recommendations": [...]
  },
  "alert_created": true,
  "timestamp": "2025-10-28T10:35:42.123456"
}
```

**Response Fields:**
- `success` - Operation success status
- `insight_id` - UUID of created insight
- `city` - City name
- `country_code` - Country code
- `insight` - Generated insight object
- `alert_created` - Whether alert was created
- `timestamp` - Completion timestamp

**Error Response:**
```json
{
  "success": false,
  "error": "Failed to analyze city data: connection timeout",
  "timestamp": "2025-10-28T10:30:00"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Bristol",
    "country_code": "GB",
    "success_criteria": "Achieve net zero by 2030 through renewable energy"
  }'
```

**Performance:** 2-5 minutes

**Important Notes:**
- This is an expensive operation - use sparingly
- Results are cached and accessible via fast endpoints
- Consider running as background job for multiple cities
- Rate limiting may apply (see Rate Limiting section)

---

### POST /api/query

**Description:** Query MindsDB agent for data analysis

**Use Case:** Ad-hoc data queries, exploratory analysis

**Request Body:**
```json
{
  "query": "How many records are in service19_onboarding_data?",
  "conversation_history": []
}
```

**Request Fields:**
- `query` (required) - Natural language query
- `conversation_history` (optional) - Previous conversation context

**Response:**
```json
{
  "success": true,
  "response": "The service19_onboarding_data table contains 1,247 records. The data includes onboarding information from 23 cities across the UK, with Bristol and Manchester having the highest record counts at 342 and 298 respectively."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Query execution failed: table not found"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8023/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many cities have data in service6_onboarding_voice?"
  }'
```

**Performance:** 10-30 seconds

---

## PostgreSQL Management Endpoints

These endpoints provide direct database access for administrative tasks.

### GET /api/postgres/tables

**Description:** List all tables in the database

**Response:**
```json
{
  "success": true,
  "data": {
    "tables": [
      "service23_data_analyst_insights",
      "service19_onboarding_data",
      "service6_onboarding_voice",
      "opportunities",
      "data_sources",
      "reports"
    ],
    "count": 6
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8023/api/postgres/tables
```

---

### GET /api/postgres/schema/{table}

**Description:** Get schema information for a specific table

**Path Parameters:**
- `table` (required) - Table name

**Response:**
```json
{
  "success": true,
  "data": {
    "table_name": "service23_data_analyst_insights",
    "columns": [
      {
        "name": "id",
        "type": "uuid",
        "nullable": false,
        "default": "gen_random_uuid()"
      },
      {
        "name": "city",
        "type": "character varying(255)",
        "nullable": false,
        "default": null
      },
      {
        "name": "confidence_score",
        "type": "numeric(3,2)",
        "nullable": true,
        "default": null
      }
    ]
  }
}
```

**cURL Example:**
```bash
curl http://localhost:8023/api/postgres/schema/service23_data_analyst_insights
```

---

### POST /api/postgres/add-column

**Description:** Add a new column to a table

**Request Body:**
```json
{
  "table": "service19_onboarding_data",
  "column_name": "sustainability_score",
  "column_type": "INTEGER",
  "default_value": "0"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Column 'sustainability_score' added successfully",
  "data": {
    "table": "service19_onboarding_data",
    "column": "sustainability_score",
    "type": "INTEGER"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8023/api/postgres/add-column \
  -H "Content-Type: application/json" \
  -d '{
    "table": "service19_onboarding_data",
    "column_name": "sustainability_score",
    "column_type": "INTEGER",
    "default_value": "0"
  }'
```

---

## Data Models

### ChatQueryRequest

```typescript
{
  query: string  // Natural language query
}
```

### ChatResponse

```typescript
{
  reply: string           // One-line summary
  replySummary: string    // Detailed paragraph
  table: string           // Source table name
  id: string             // UUID of record
}
```

### InsightSummary

```typescript
{
  id: string
  city: string
  country_code: string
  insight_summary: string
  confidence_score?: number  // 0.0 to 1.0
  created_at?: string       // ISO 8601 timestamp
}
```

### InsightDetail

```typescript
{
  id: string
  city: string
  country_code: string
  success_criteria?: string
  insight_summary: string
  detailed_analysis: string
  data_sources_used?: string[]
  confidence_score?: number
  recommendations?: Recommendation[]
  created_at?: string
  updated_at?: string
  alert_sent?: boolean
  alert_id?: string
}
```

### Recommendation

```typescript
{
  priority: "high" | "medium" | "low"
  category: string
  action: string
  expected_impact: string
  timeline: string
  estimated_cost?: string
  roi_years?: number
}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input, missing required fields |
| 404 | Not Found | Resource (city, insight) not found |
| 500 | Internal Server Error | Database errors, service failures |
| 503 | Service Unavailable | Database connection failed |

### Common Errors

#### 400 - City Not Identified
```json
{
  "detail": "Could not identify a city in your query. Please mention a specific city name."
}
```

**Cause:** Natural language parser couldn't extract city name

**Solution:** Include a specific city name in your query

#### 404 - No Insights Found
```json
{
  "detail": "No insights found for Manchester, GB"
}
```

**Cause:** No cached insights exist for the specified city

**Solution:** Generate insights using `/api/analyze/city-insights`

#### 500 - Database Error
```json
{
  "detail": "Database error: connection timeout"
}
```

**Cause:** PostgreSQL connection issues

**Solution:** Check database connectivity, verify credentials

---

## Rate Limiting

### Current Implementation

**Status:** Not yet implemented

### Planned Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Fast endpoints | 1000 requests | per minute |
| Slow endpoints | 10 requests | per hour |
| Admin endpoints | 100 requests | per hour |

**Headers (future):**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1640995200
```

---

## Natural Language Query Parsing

The API includes intelligent natural language parsing for city and country queries.

### Supported Cities

```
Bristol, Manchester, Birmingham, Leeds, Edinburgh
London, Glasgow, Liverpool, Newcastle, Sheffield
Nottingham, Boston, Dubai, Singapore, Tokyo
```

### Supported Countries

| Query Terms | Country Code |
|-------------|--------------|
| UK, Britain, England, Scotland, Wales, United Kingdom | GB |
| USA, America, United States | US |
| UAE, Dubai, Emirates | AE |
| Singapore | SG |
| Japan | JP |

### Query Examples

**City Queries:**
- "Show me the insights for Bristol"
- "What about Manchester?"
- "Tell me about London's analysis"
- "Edinburgh data"

**Country Queries:**
- "Show me cities in the UK"
- "What cities are available in Great Britain?"
- "List all USA cities"
- "Show me United States"

### Parser Behavior

1. **Case Insensitive:** "BRISTOL" = "bristol" = "Bristol"
2. **Flexible Matching:** Looks for city/country keywords anywhere in query
3. **Default Country:** Assumes GB if no country specified
4. **First Match:** Returns first recognized city in the query

---

## Database Schema

### service23_data_analyst_insights

```sql
CREATE TABLE service23_data_analyst_insights (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Location identifiers
    city VARCHAR(255) NOT NULL,
    country_code VARCHAR(2) NOT NULL,

    -- Success criteria reference
    success_criteria TEXT,

    -- Insight content
    insight_summary TEXT NOT NULL,
    detailed_analysis TEXT NOT NULL,

    -- Metadata
    data_sources_used JSONB DEFAULT '[]'::jsonb,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    recommendations JSONB DEFAULT '[]'::jsonb,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Alert tracking
    alert_sent BOOLEAN DEFAULT FALSE,
    alert_id VARCHAR(255),

    -- Indexes
    CONSTRAINT valid_confidence CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1))
);

-- Indexes for performance
CREATE INDEX idx_insights_city_country ON service23_data_analyst_insights(city, country_code);
CREATE INDEX idx_insights_created_at ON service23_data_analyst_insights(created_at DESC);
CREATE INDEX idx_insights_confidence ON service23_data_analyst_insights(confidence_score DESC);
```

**Key Columns:**
- `id` - UUID primary key
- `city` - City name (indexed)
- `country_code` - ISO country code (indexed)
- `insight_summary` - Brief summary for quick display
- `detailed_analysis` - Full analysis text
- `confidence_score` - AI confidence (0.0 to 1.0)
- `recommendations` - JSONB array of recommendations
- `created_at` - Indexed for sorting by recency

---

## Examples & Use Cases

### Use Case 1: Dashboard Display

**Scenario:** Display recent city insights on a dashboard

```bash
# Get 10 most recent insights
curl http://localhost:8023/insights/recent?limit=10

# Display on dashboard with city names, summaries, and confidence scores
```

### Use Case 2: City Detail Page

**Scenario:** Show all information for a specific city

```bash
# Step 1: Get latest insight summary
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Bristol"}'

# Step 2: Get full details using the returned UUID
curl http://localhost:8023/insights/550e8400-e29b-41d4-a716-446655440000

# Step 3: Get historical insights
curl "http://localhost:8023/insights/city/Bristol?limit=5"
```

### Use Case 3: Country Overview for Investors

**Scenario:** Investor wants to see all UK cities

```bash
# Get latest insight for UK
curl -X POST http://localhost:8023/chat/cities \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me UK cities"}'

# Get recent UK insights
curl http://localhost:8023/insights/recent?limit=20
# Filter by country_code=GB in application
```

### Use Case 4: Generate Insights for New City

**Scenario:** Onboard a new city with AI analysis

```bash
# Step 1: Generate insight (slow - 2-5 min)
curl -X POST http://localhost:8023/api/analyze/city-insights \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Edinburgh",
    "country_code": "GB",
    "success_criteria": "Achieve net zero by 2030"
  }'

# Wait for completion...

# Step 2: Query the cached insight (fast)
curl -X POST http://localhost:8023/chat/city \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me Edinburgh"}'
```

### Use Case 5: Scheduled Updates

**Scenario:** Nightly job to update all city insights

```python
import requests
import time

cities = [
    {"city": "Bristol", "country_code": "GB"},
    {"city": "Manchester", "country_code": "GB"},
    {"city": "London", "country_code": "GB"}
]

for city_data in cities:
    response = requests.post(
        "http://localhost:8023/api/analyze/city-insights",
        json=city_data
    )

    if response.json()["success"]:
        print(f"Updated {city_data['city']}")

    time.sleep(300)  # Wait 5 min between requests
```

---

## Performance Characteristics

### Response Times

| Endpoint Category | Typical Response Time | Notes |
|-------------------|----------------------|-------|
| Health checks | 10-50ms | Very fast |
| Cached insights | 50-100ms | Database query + formatting |
| Recent insights | 20-50ms | Indexed query |
| AI generation | 2-5 minutes | Multiple AI calls + data gathering |
| MindsDB query | 10-30 seconds | Depends on query complexity |

### Optimization Tips

1. **Use Cached Endpoints:** Always prefer `/chat/city` over `/api/analyze/city-insights` for user-facing queries
2. **Limit Results:** Use appropriate `limit` parameters to reduce data transfer
3. **Batch Requests:** When generating multiple insights, space them out to avoid overwhelming the system
4. **Cache Client-Side:** Cache responses in your application for 5-10 minutes
5. **Use UUIDs:** When you have a UUID, use `/insights/{id}` directly instead of searching

### Database Connection Pooling

The service uses connection pooling with the following defaults:
- **Min connections:** 5
- **Max connections:** 20
- **Connection timeout:** 30 seconds
- **Idle timeout:** 10 minutes

---

## Deployment

### Requirements

- Python 3.11+
- PostgreSQL 16.3+
- 2GB RAM minimum
- Port 8023 available

### Environment Variables

```bash
# Database
DB_HOST=urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com
DB_PORT=5432
DB_NAME=urbanzero-db
DB_USER=urbanzero_app
DB_PASSWORD=UrbanZero2024$Secure

# Service
PORT=8023
HOST=0.0.0.0

# AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional
ARIZE_API_KEY=...
ARIZE_SPACE_ID=...
```

### Start Service

```bash
# Direct
python api_server.py

# With PM2
pm2 start api_server.py --interpreter python --name service23-api

# With systemd
sudo systemctl start service23
```

### Health Check

```bash
# Verify service is running
curl http://localhost:8023/health

# Expected response
{
  "status": "healthy",
  "database": "connected",
  "insights_count": 42
}
```

### Monitoring

**Key Metrics:**
- Response time for `/chat/city` (should be < 100ms)
- Database connection status
- Insights count growth
- Error rate

**Logging:**
- Service logs to stdout
- Use PM2 or systemd for log management
- Monitor for database connection errors

---

## Interactive Documentation

### Swagger UI

**URL:** http://localhost:8023/docs

**Features:**
- Interactive endpoint testing
- Request/response examples
- Model schemas
- Try it out functionality

### ReDoc

**URL:** http://localhost:8023/redoc

**Features:**
- Clean, readable documentation
- Searchable content
- Code samples
- Printable format

---

## Support & Contact

**Service:** Service23 - Data Analyst Agent API
**Version:** 2.0.0
**Port:** 8023
**Status:** ✅ Production Ready

**Documentation:**
- API Docs (this file): `/docs/API.md`
- Quick Start: `/QUICK_START.md`
- cURL Commands: `/CURL_COMMANDS_PORT_8023.md`
- Consolidation Summary: `/SERVICE_CONSOLIDATION_SUMMARY.md`

**Interactive:**
- Swagger UI: http://localhost:8023/docs
- ReDoc: http://localhost:8023/redoc

---

## Changelog

### v2.0.0 (2025-10-28)
- ✅ Consolidated separate microservice into unified API
- ✅ All endpoints now on port 8023
- ✅ Added 5 cached insights query endpoints
- ✅ Enhanced health check with database status
- ✅ Improved natural language query parsing
- ✅ Comprehensive API documentation

### v1.0.0 (2025-10-27)
- Initial release with AI generation endpoints
- MindsDB agent integration
- PostgreSQL management tools

---

**Last Updated:** 2025-10-28
**Document Version:** 2.0.0
