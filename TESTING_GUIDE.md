# MindsDB Data Analyst Agent - Testing Guide

## Overview
The MindsDB Data Analyst Agent queries SERVICE19 onboarding data using Claude SDK and MindsDB.

## Recent Improvements

### Rate Limit Handling Enhancement
**Problem**: Hitting Anthropic API rate limits during complex queries  
**Solution**: Improved exponential backoff retry mechanism

#### Configuration Changes:
- **Max Retries**: 3 → 5
- **Backoff Multiplier**: 2x → 3x  
- **Wait Times**: 2s, 4s, 8s → 3s, 6s, 12s, 24s, 48s
- **Total Wait**: 14s → 93s before failure

This provides significantly more tolerance for transient rate limit errors.

### Schema Updates
Updated column names to match current database schema:
- `id` → `data_id`
- `onboarding_id` → `source_id`
- `url` → `download_url`
- `fetched_at` → `download_timestamp`
- `success` → `download_success`
- `http_status` → `http_status_code`
- `file_type` → `data_format`
- `content_size` → `file_size_bytes`

## Prerequisites

### 1. Environment Variables
Add to `.env` file:
```bash
ANTHROPIC_API_KEY=your_key_here
```

### 2. MindsDB Service
MindsDB must be running on port 47334:
```bash
# Check if MindsDB is running
curl http://localhost:47334/api/status

# Or start MindsDB
# (installation/startup commands depend on your setup)
```

### 3. Python Dependencies
```bash
pip install anthropic httpx python-dotenv
```

## Running Tests

### Test 1: Simple Query
```bash
python mindsdb_agent.py "How many records are in the database?"
```

### Test 2: Zebra Crossing Query (Original Issue)
```bash
python mindsdb_agent.py "find the location of every zebra crossing mentioned in our dataset"
```

### Test 3: Interactive Mode
```bash
python mindsdb_agent.py
# Then type queries interactively
```

### Test 4: Multiple Queries
```bash
python test_simple_agent.py
```

## Expected Behavior

### With Rate Limits:
```
⚠ Rate limit hit. Waiting 3s before retry 1/5...
⚠ Rate limit hit. Waiting 6s before retry 2/5...
⚠ Rate limit hit. Waiting 12s before retry 3/5...
```

The agent will automatically retry up to 5 times with increasing delays.

### Without Rate Limits:
- Agent queries MindsDB
- Returns formatted results
- Exports large result sets (>50 rows) to CSV automatically

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
Add the key to your `.env` file in the server_c directory.

### "Connection refused" or timeout
MindsDB service is not running on port 47334.

### "Rate limit exceeded after 5 retries"
API quota exhausted. Wait a few minutes and try again, or:
- Reduce query complexity
- Use simpler test queries first
- Check your Anthropic API tier/limits

### "Query timeout"
Query took too long. The agent will suggest:
- Adding LIMIT clauses
- Avoiding SELECT * on large tables
- Using aggregate queries instead of raw data

## Success Criteria

✅ Agent connects to MindsDB  
✅ Executes SQL queries successfully  
✅ Handles rate limits gracefully with retries  
✅ Exports large results to CSV  
✅ Returns formatted, readable output  

## Additional Notes

- The agent avoids `raw_data` and `error_details` columns to prevent token overflow
- Results with >50 rows are automatically exported to `results/` directory
- Alert creation can be disabled with `--no-alerts` flag
