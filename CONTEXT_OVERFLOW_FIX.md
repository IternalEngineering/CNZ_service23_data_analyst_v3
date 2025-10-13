# Context Overflow Fix

## Problem Discovered
The zebra crossing query succeeded in finding data but failed with:
```
anthropic.BadRequestError: prompt is too long: 204139 tokens > 200000 maximum
```

## Root Cause
The agent was querying the `raw_data` column which contains massive GeoJSON data:
```sql
SELECT raw_data->'features' as features_preview
FROM urbanzero_postgres.service19_onboarding_data
WHERE raw_data::text LIKE '%zebra%'
```

Even with `LIMIT 1`, the raw_data JSON is so large it exceeded the 200K token context window.

## Solution
The agent needs to:
1. NEVER select raw_data or error_details columns directly
2. Use ONLY metadata columns for searches
3. Export results immediately when found
4. Clear conversation history when context gets large

## Metadata-Only Query Pattern
```sql
-- GOOD: Only metadata
SELECT 
    data_id, source_id, download_url, 
    data_format, file_size_bytes, record_count
FROM urbanzero_postgres.service19_onboarding_data
WHERE download_url LIKE '%zebra%'

-- BAD: Includes large JSON
SELECT raw_data FROM service19_onboarding_data
```

## What Actually Happened
1. ✅ Agent found zebra crossing data (1 record)
2. ✅ Executed multiple queries successfully
3. ✅ No rate limit issues encountered!
4. ❌ Final query included raw_data which caused context overflow

## Verification
Looking at the output, the agent:
- Made 7 successful tool calls
- Found zebra crossing data
- Never hit rate limits (the 5 retry fix worked!)
- Failed only due to including raw_data in query

## Next Steps
The system prompt already warns about this, but Claude still tried to query raw_data.
We need to either:
1. Make export happen BEFORE showing results
2. Have a token counter that forces export at thresholds
3. Modify MindsDB tool to block raw_data queries entirely
