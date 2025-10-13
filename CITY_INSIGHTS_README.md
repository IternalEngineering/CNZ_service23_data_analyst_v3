# City Insights Analyzer - Quick Start Guide

## What It Does

This system uses an AI data analyst agent to:
1. **Query** the `service6_onboarding_voice` table for success criteria
2. **Gather** data from multiple disparate sources (opportunities, data_sources, service19 data, etc.)
3. **Connect** information across these sources to identify patterns and insights
4. **Generate** actionable recommendations relevant to the success criteria
5. **Store** insights in `service23_data_analyst_insights` table
6. **Create** alerts on the web platform with the results

## Files Created

### Core Implementation
- **`city_insights_analyzer.py`** - Main analyzer using Claude agent to connect disparate data
- **`api_server.py`** - FastAPI server with `/api/analyze/city-insights` endpoint (UPDATED)
- **`create_insights_table.sql`** - Database schema for insights storage
- **`run_migration.py`** - Script to create the insights table

### Documentation & Testing
- **`DATA_ANALYST_INSIGHT_API.md`** - Complete API documentation
- **`test_city_insights.py`** - Python test script (direct, no API)
- **`test_api_curl.sh`** - Bash test script with curl commands
- **`test_api_curl.bat`** - Windows batch test script
- **`CITY_INSIGHTS_README.md`** - This file

## Quick Start (3 Steps)

### Step 1: Run Database Migration

```bash
python run_migration.py
```

This creates the `service23_data_analyst_insights` table.

### Step 2: Start API Server

```bash
python api_server.py
```

Server will start on `http://localhost:8012`

### Step 3: Test with Curl

```bash
curl -X POST http://localhost:8012/api/analyze/city-insights \
    -H "Content-Type: application/json" \
    -d '{
      "city": "Bristol",
      "country_code": "GB",
      "success_criteria": "Achieve net zero by 2030 through renewable energy"
    }'
```

**This matches your original request format!**

## Alternative: Use Test Scripts

### Linux/Mac
```bash
bash test_api_curl.sh
```

### Windows
```bat
test_api_curl.bat
```

### Python (Direct Test)
```bash
python test_city_insights.py
```

## How It Works

### 1. Data Collection Phase
The agent queries multiple tables:
- `service6_onboarding_voice` - For success criteria (text_responses field)
- `opportunities` - Investment opportunities
- `data_sources` - Available data sources
- `service19_onboarding_data` - Collected city data
- `service19_onboarding_agent_sources` - Data source metadata

### 2. Analysis Phase
Claude agent:
- Connects information across disparate sources
- Identifies patterns and gaps
- Evaluates against success criteria
- Generates actionable insights with confidence scores

### 3. Storage Phase
Results stored in `service23_data_analyst_insights`:
```sql
{
  id: UUID,
  city: "Bristol",
  country_code: "GB",
  success_criteria: "...",
  insight_summary: "Brief summary",
  detailed_analysis: "Comprehensive analysis",
  data_sources_used: ["table1", "table2", ...],
  confidence_score: 0.85,
  recommendations: ["Action 1", "Action 2", ...],
  created_at: timestamp,
  alert_sent: true
}
```

### 4. Alert Phase
Creates web alert with:
- Insight summary
- Confidence score
- Top 3 recommendations
- Link to full analysis (via insight_id)

## API Response Format

```json
{
  "success": true,
  "insight_id": "uuid-here",
  "city": "Bristol",
  "country_code": "GB",
  "insight": {
    "insight_summary": "Brief summary",
    "detailed_analysis": "Full analysis connecting data sources",
    "data_sources_used": ["service6_onboarding_voice", "opportunities"],
    "confidence_score": 0.85,
    "recommendations": ["Rec 1", "Rec 2", "Rec 3"]
  },
  "alert_created": true,
  "timestamp": "2025-10-09T12:34:56Z"
}
```

## Querying Results

### View All Insights
```sql
SELECT id, city, country_code, insight_summary, confidence_score, created_at
FROM service23_data_analyst_insights
ORDER BY created_at DESC
LIMIT 10;
```

### View Specific Insight
```sql
SELECT *
FROM service23_data_analyst_insights
WHERE id = 'your-insight-id';
```

### View Insights by City
```sql
SELECT *
FROM service23_data_analyst_insights
WHERE city = 'Bristol' AND country_code = 'GB'
ORDER BY created_at DESC;
```

### View High-Confidence Insights
```sql
SELECT city, insight_summary, confidence_score, created_at
FROM service23_data_analyst_insights
WHERE confidence_score >= 0.8
ORDER BY confidence_score DESC, created_at DESC;
```

## Configuration

### Environment Variables
- `AGENT_PORT` - API server port (default: 8012)
- `ANTHROPIC_API_KEY` - Claude API key (required)
- `POSTGRES_HOST` - PostgreSQL host
- `POSTGRES_DATABASE` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `CNZ_API_KEY` - API key for creating alerts

### Database Connection
The system connects to PostgreSQL using credentials from `.env` file:
```env
POSTGRES_HOST=urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DATABASE=urbanzero-db
POSTGRES_USER=urbanzero_app
POSTGRES_PASSWORD=your-password
```

## Troubleshooting

### Migration Fails
- Check PostgreSQL connection in `.env`
- Verify user has CREATE TABLE permissions
- Try running SQL manually: `psql -f create_insights_table.sql`

### API Returns Errors
- Check ANTHROPIC_API_KEY is set
- Verify PostgreSQL is accessible
- Check agent has data to analyze (run queries on source tables)

### No Alerts Created
- Verify CNZ_API_KEY is set
- Check alert creator base URL
- Test alert creation separately: `python alert_creator.py`

### Agent Times Out
- Long analyses may take 2-5 minutes
- Check API logs for progress
- Consider increasing timeout in analyzer

## Next Steps

1. **Test with different cities**: Try London, Manchester, etc.
2. **Customize success criteria**: Adjust to match specific goals
3. **Add more data sources**: Extend agent to query additional tables
4. **Schedule regular analysis**: Set up cron job for automated insights
5. **Build dashboard**: Visualize insights and trends over time

## Architecture Diagram

```
┌─────────────┐
│   Client    │
│  (curl/web) │
└──────┬──────┘
       │ POST /api/analyze/city-insights
       ▼
┌─────────────────────────────┐
│      api_server.py          │
│   (FastAPI on :8012)        │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  city_insights_analyzer.py  │
│  (Claude Agent Orchestrator)│
└──────┬──────────────────────┘
       │
       ├─────────┬─────────┬─────────┐
       ▼         ▼         ▼         ▼
  ┌────────┐ ┌────────┐ ┌─────┐ ┌──────┐
  │service6│ │service │ │opps.│ │data_ │
  │onboard.│ │  19    │ │     │ │source│
  └────────┘ └────────┘ └─────┘ └──────┘
       │
       └──────┬───────────────────────┐
              ▼                       ▼
      ┌───────────────┐      ┌──────────────┐
      │service23_     │      │ Alert on Web │
      │insights table │      │   Platform   │
      └───────────────┘      └──────────────┘
```

## Support

For issues or questions:
1. Check `DATA_ANALYST_INSIGHT_API.md` for detailed documentation
2. Review logs in console output
3. Test individual components (migration, API, agent)
4. Verify environment variables and database access

## Credits

Built for UrbanZero platform using:
- Anthropic Claude Sonnet 4.5 (AI analysis)
- FastAPI (API framework)
- PostgreSQL (data storage)
- asyncpg (async database driver)
