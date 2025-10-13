# Data Analyst Insight API

## Overview
This API endpoint uses the data analyst agent to analyze city data across disparate database sources, connects information to generate insights relevant to success criteria, and stores results with alert notifications.

## Endpoint

```bash
POST http://localhost:8012/api/analyze/city-insights
```

**Note:** The API runs on port 8012 (configurable via `AGENT_PORT` environment variable)

## Request Format

```json
{
  "city": "Bristol",
  "country_code": "GB",
  "success_criteria": "Achieve net zero by 2030 through renewable energy"
}
```

### Parameters

- **city** (required): Name of the city to analyze
- **country_code** (required): ISO 3166-1 alpha-2 country code (e.g., "GB", "US")
- **success_criteria** (optional): Specific success criteria to evaluate. If not provided, uses default criteria from onboarding data.

## Response Format

```json
{
  "success": true,
  "insight_id": "uuid-here",
  "city": "Bristol",
  "country_code": "GB",
  "insight": {
    "summary": "Brief summary of the insight",
    "detailed_analysis": "Comprehensive analysis connecting disparate data sources",
    "data_sources_used": ["service6_onboarding_voice", "opportunities", "data_sources"],
    "success_criteria": "Achieve net zero by 2030 through renewable energy",
    "confidence_score": 0.85,
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "alert_created": true,
  "timestamp": "2025-10-09T12:34:56Z"
}
```

## Data Sources Priority

The agent analyzes data from multiple sources in the following priority order:

1. **Primary**: `datasource_postgres.public.service6_onboarding_voice` (text_responses field - success criteria)
2. **Secondary**: City-specific data sources
3. **Tertiary**: General opportunities and data sources

## Database Storage

Insights are stored in: `datasource_postgres.public.service23_data_analyst_insights`

### Schema

```sql
CREATE TABLE service23_data_analyst_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city VARCHAR(255) NOT NULL,
    country_code VARCHAR(2) NOT NULL,
    success_criteria TEXT,
    insight_summary TEXT NOT NULL,
    detailed_analysis TEXT NOT NULL,
    data_sources_used JSONB,
    confidence_score DECIMAL(3,2),
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    alert_sent BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_city_country ON service23_data_analyst_insights(city, country_code);
CREATE INDEX idx_created_at ON service23_data_analyst_insights(created_at DESC);
```

## Alert System

When an insight is generated, an alert is created in the web application containing:
- Insight summary
- Confidence score
- Link to detailed analysis
- Recommended actions

## Setup Instructions

### 1. Install Dependencies

```bash
# Make sure you're in the service23 directory
cd server_c/service23

# Activate virtual environment (if using uv)
uv venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows

# Install Python packages
pip install anthropic asyncpg httpx python-dotenv fastapi uvicorn
```

### 2. Run Database Migration

```bash
# Create the insights table in PostgreSQL
python run_migration.py
```

Expected output:
```
============================================================
Database Migration: Create service23_data_analyst_insights
============================================================
✓ Connected to PostgreSQL
✓ Table verified with 12 columns
```

### 3. Start the API Server

```bash
# Start on port 8012 (default)
python api_server.py

# OR specify custom port
AGENT_PORT=8012 python api_server.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8012
```

## Example cURL Commands

### Basic Usage (with explicit success criteria)

```bash
curl -X POST http://localhost:8012/api/analyze/city-insights \
    -H "Content-Type: application/json" \
    -d '{
      "city": "Bristol",
      "country_code": "GB",
      "success_criteria": "Achieve net zero by 2030 through renewable energy"
    }'
```

**This is the recommended format matching your original request!**

### With Default Success Criteria (auto-fetch from database)

```bash
curl -X POST http://localhost:8012/api/analyze/city-insights \
    -H "Content-Type: application/json" \
    -d '{
      "city": "Bristol",
      "country_code": "GB"
    }'
```

### Different City Example

```bash
curl -X POST http://localhost:8012/api/analyze/city-insights \
    -H "Content-Type: application/json" \
    -d '{
      "city": "London",
      "country_code": "GB",
      "success_criteria": "Reduce carbon emissions by 50% by 2030"
    }'
```

### Using Test Scripts

```bash
# Linux/Mac
bash test_api_curl.sh

# Windows
test_api_curl.bat

# Python test (direct, no API)
python test_city_insights.py
```

## Implementation Details

### Agent Flow

1. **Input Validation**: Validate city and country_code parameters
2. **Data Collection**: Query multiple database sources
   - Retrieve success criteria from onboarding data
   - Fetch city-specific opportunities
   - Collect relevant data sources
3. **Analysis**: Use Data Analyst Agent to:
   - Connect information across disparate sources
   - Identify patterns and insights
   - Evaluate against success criteria
   - Generate recommendations
4. **Storage**: Save insight to database
5. **Alert**: Create notification in web application
6. **Response**: Return formatted result

### Error Handling

The API handles the following error cases:

- Missing required parameters (400 Bad Request)
- Invalid country code format (400 Bad Request)
- Database connection failures (500 Internal Server Error)
- Agent execution timeout (504 Gateway Timeout)
- No data found for city (404 Not Found)

### Timeout Configuration

- Default timeout: 120 seconds
- Can be adjusted via environment variable: `ANALYST_TIMEOUT`

## Dependencies

- FastAPI
- CrewAI agents
- Snowflake connector
- PostgreSQL connection
- OpenAI API (for agent)

## Environment Variables

```bash
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=datasource_postgres
SNOWFLAKE_SCHEMA=public
SNOWFLAKE_WAREHOUSE=your_warehouse
OPENAI_API_KEY=your_openai_key
```

## Testing

### Health Check

```bash
curl http://localhost:8011/health
```

### Agent Status

```bash
curl http://localhost:8011/api/agents/status
```

## Monitoring

Monitor the agent execution via logs:

```bash
pm2 logs service23
```

Or if running directly:

```bash
tail -f logs/service23.log
```

## Performance Considerations

- Query optimization for large datasets
- Caching of frequently accessed city data
- Rate limiting to prevent abuse
- Async processing for long-running analyses

## Future Enhancements

- [ ] Support for multiple cities in single request
- [ ] Historical insight comparison
- [ ] Real-time data source integration
- [ ] Webhook notifications for insight generation
- [ ] Dashboard visualization integration
