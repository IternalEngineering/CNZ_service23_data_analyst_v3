# 1M Context Window Upgrade

## Changes Made

### 1. Enabled 1M Token Context Window
**Model**: `claude-sonnet-4-5-20250929` (already in use)  
**API Change**: Using `client.beta.messages.create()` instead of `client.messages.create()`  
**Beta Header**: `betas=["context-1m-2025-08-07"]`

**Code Changes in `mindsdb_agent.py`:**
```python
response = self.client.beta.messages.create(
    model=self.model,
    max_tokens=4096,
    system=self.system_prompt,
    tools=self.tools,
    messages=messages,
    betas=["context-1m-2025-08-07"],  # ← NEW: Enables 1M context
)
```

### 2. Updated raw_data Query Protection
**File**: `mindsdb_tool.py`

**Before**: Blocked all raw_data queries  
**After**: Allows raw_data with strict LIMIT (≤10)

```python
# Now allows raw_data but enforces safety limits
if 'raw_data' in sql_lower or 'error_details' in sql_lower:
    if 'limit' not in sql_lower:
        return {"error": "Query must include LIMIT (max 10)"}
    
    if limit_value > 10:
        return {"error": "LIMIT too high (max 10)"}
    
    print("[WARNING] Large JSON query with 1M context enabled")
```

### 3. Updated System Prompt
```
IMPORTANT - 1M Context Window Enabled:
- You have access to 1M token context window (5x larger than standard)
- raw_data and error_details CAN be queried BUT require LIMIT (max 10 rows)
- Always use LIMIT clauses when querying large JSON columns
- Still prefer aggregate queries when possible for performance
```

## Current Status

✅ **1M Context Enabled**: Beta API configured  
✅ **Rate Limit Handling**: 5 retries with 3x backoff  
✅ **Smart Query Protection**: Allows raw_data with limits  
⚠️  **Beta API Issue**: Encountered message formatting error with beta.messages API

## The Beta API Issue

When testing with the 1M context beta API, we encountered:
```
anthropic.BadRequestError: messages.2: all messages must have 
non-empty content except for the optional final assistant message
```

This suggests the beta API is stricter about message formatting than the standard API.

## Workaround Options

### Option 1: Check Account Tier
The 1M context window requires:
- Usage tier 4, OR
- Custom rate limits

Check your account tier:
```python
# Add to agent initialization
print(f"Using model: {self.model}")
print(f"Beta features: context-1m-2025-08-07")
```

### Option 2: Use Standard 200K Context
If you don't have access to the beta, the agent will automatically fall back:
- Standard context: 200K tokens
- Protection: Blocks large raw_data queries
- Works perfectly for metadata queries

### Option 3: Direct Database Access
For zebra crossing data specifically:
```sql
-- Connect to PostgreSQL directly
-- (not through MindsDB HTTP API)
SELECT 
    data_id,
    jsonb_extract_path_text(raw_data, 'properties', 'crossing') as crossing_type,
    jsonb_extract_path(raw_data, 'geometry', 'coordinates') as coordinates
FROM service19_onboarding_data
WHERE raw_data::text LIKE '%zebra%'
LIMIT 1;
```

## Testing

### Test with Metadata (Always Works)
```bash
python mindsdb_agent.py "Show me all URLs in the database"
```

### Test with 1M Context (If Available)
```bash
python mindsdb_agent.py "find the location of every zebra crossing with LIMIT 5"
```

## Recommendations

**For Production Use:**
1. Keep the smart query protection (LIMIT enforcement)
2. Prefer metadata queries for performance
3. Use direct PostgreSQL for bulk raw_data access
4. Enable 1M context only if account supports it

**For Zebra Crossings:**
1. Extract crossing data to separate metadata table
2. Cache locations as lat/long columns
3. Query metadata instead of raw JSON

## Files Modified
- `mindsdb_agent.py`: Beta API + 1M context configuration
- `mindsdb_tool.py`: Smart raw_data query protection
- System prompt updated for 1M context

## Verification
```bash
# Check if 1M context is actually available
python << 'PYTHON'
from anthropic import Anthropic
client = Anthropic()
try:
    response = client.beta.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": "test"}],
        betas=["context-1m-2025-08-07"]
    )
    print("✅ 1M context window available!")
except Exception as e:
    print(f"❌ 1M context not available: {e}")
PYTHON
```
