# Service23 - MindsDB Data Analyst Agent

AI-powered data analyst agent that queries SERVICE19 onboarding data using Claude SDK with direct PostgreSQL access.

## Overview

Service23 provides intelligent data analysis capabilities with:
- **Claude SDK Integration**: Uses Anthropic's Claude Sonnet 4.5 for natural language queries
- **Direct PostgreSQL Access**: Bypasses MindsDB HTTP API for large data queries
- **Rate Limit Handling**: 5 retries with exponential backoff (3s, 6s, 12s, 24s, 48s)
- **Smart Query Protection**: Prevents context overflow on large JSON fields

## Key Features

### 1. Dual Query System
- **MindsDB Tool**: Fast metadata queries through HTTP API
- **PostgreSQL Direct Tool**: Direct database access for raw_data queries
- **Export Tool**: Save large result sets to CSV

### 2. Context Overflow Protection
- Automatically blocks queries that would exceed token limits
- Enforces LIMIT clauses on large JSON columns
- Truncates large results with smart summaries

### 3. Rate Limit Resilience
- 5 retry attempts (up from 3)
- 3x exponential backoff (up from 2x)
- Total wait time: 93 seconds (up from 14s)

## Quick Start

### Prerequisites
```bash
# Install dependencies
pip install anthropic asyncpg httpx python-dotenv requests

# Configure environment
cp .env.example .env
# Edit .env and add:
# - ANTHROPIC_API_KEY
# - PostgreSQL credentials (optional, has defaults)
```

### Setup SSH Tunnel (for MindsDB)

**See `SETUP_GUIDE.md` for complete setup instructions**

**Quick Setup:**
```bash
# Option 1: PowerShell (Recommended)
.\setup_tunnel.ps1

# Option 2: Batch Script
start_tunnel.bat

# Option 3: Manual SSH
ssh -i C:\Users\chriz\.ssh\cnz-staging-key.pem -N -L 47334:localhost:47334 ec2-user@18.168.195.169
```

**Verify Connection:**
```bash
# Check MindsDB status
curl http://localhost:47334/api/status

# Run comprehensive test suite
python test_mindsdb_connection.py
```

**Access MindsDB:**
- HTTP API: http://localhost:47334
- Web Interface: http://localhost:47334 (in browser)

### Run Agent

**Simple Query:**
```bash
python mindsdb_agent.py "How many records are in the database?"
```

**Direct PostgreSQL Query:**
```bash
python mindsdb_agent.py "Use the direct PostgreSQL tool to find zebra crossings"
```

**Interactive Mode:**
```bash
python mindsdb_agent.py
# Then type queries interactively
```

## Architecture

### Tools Available

1. **query_mindsdb**
   - Fast queries through MindsDB HTTP API
   - Best for: Metadata, counts, simple queries
   - Limit: 200K tokens via API responses

2. **query_postgres_direct** ⭐ NEW
   - Direct PostgreSQL connection via asyncpg
   - Best for: raw_data queries, large GeoJSON
   - Limit: Only by query LIMIT clause

3. **export_query_results**
   - Exports results to CSV files
   - Best for: >50 row result sets
   - Location: `results/` directory

### Database Schema

**SERVICE19 Tables:**
- `service19_onboarding_data` - Main data table with raw_data JSON
- `service19_onboarding_agent_sources` - Source metadata with city info

**Key Columns:**
```
service19_onboarding_data:
- data_id, source_id, download_url
- download_success, http_status_code, data_format
- file_size_bytes, record_count
- raw_data (JSONB) - Large GeoJSON data
- error_details (TEXT) - Error messages
```

## Success Story: Zebra Crossings

The agent successfully found and extracted 51 zebra crossing locations from Bristol highway data:

```python
# Manual test (proven to work)
python postgres_direct_tool.py

# Results:
# - 51 features containing "zebra"
# - GPS coordinates for each crossing
# - Issue descriptions and safety concerns
# - Example: "Cars not stopping at Zebra Crossing on Long Cross"
#   Coordinates: [-2.6590910822721, 51.502250026395]
```

## Documentation

- `SETUP_GUIDE.md` - **Complete MindsDB setup and usage guide** ⭐
- `MINDSDB_SETUP.md` - MindsDB connection configuration reference
- `TESTING_GUIDE.md` - Comprehensive testing instructions
- `RATE_LIMIT_FIX_SUMMARY.md` - Rate limit improvements details
- `CONTEXT_OVERFLOW_FIX.md` - Analysis of context overflow issue
- `TEST_DIRECT_POSTGRES.md` - Direct PostgreSQL testing guide
- `1M_CONTEXT_UPGRADE.md` - 1M context window (beta) notes
- `FINAL_TEST_SUMMARY.md` - Complete test results

## Testing

### Automated Tests
```bash
python test_rate_limits.py
```

### Manual Tests
```bash
# Test 1: Simple count
python mindsdb_agent.py "How many records are in the database?"

# Test 2: URL search
python mindsdb_agent.py "Show me all URLs in the database"

# Test 3: Direct PostgreSQL
python postgres_direct_tool.py
```

## Configuration

### Environment Variables

Required:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Optional (has defaults):
```
POSTGRES_HOST=urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com
POSTGRES_PORT=5432
POSTGRES_DATABASE=urbanzero-db
POSTGRES_USER=urbanzero_app
POSTGRES_PASSWORD=UrbanZero2024$Secure
```

### MindsDB Configuration
```
MINDSDB_BASE_URL=http://localhost:47334
```

## Development

### Adding New Queries

The agent uses Claude's tool calling. Add specialized queries in `postgres_direct_tool.py`:

```python
async def query_my_custom_data(self, limit: int = 5):
    sql = """
        SELECT specific_fields
        FROM your_table
        WHERE conditions
        LIMIT $1
    """
    return await self.query(sql, [limit])
```

### Modifying System Prompt

Edit `mindsdb_agent.py` line 63 to change agent behavior.

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
Add key to `.env` file in server_c directory.

### "Connection refused on localhost:47334"
MindsDB tunnel not running. Run `setup_tunnel.ps1`.

### "Rate limit exceeded"
Agent automatically retries 5 times. If still failing, wait a few minutes.

### "Query timeout"
Query took too long. Add LIMIT clause or simplify query.

## Performance

- **Simple queries**: <2 seconds
- **Metadata queries**: 2-5 seconds
- **Direct PostgreSQL queries**: 5-15 seconds
- **Rate limit retries**: Up to 93 seconds total

## License

Proprietary - IternalEngineering/CNZ
