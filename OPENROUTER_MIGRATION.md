# OpenRouter Migration for MindsDB Agent

## Summary
Migrated `mindsdb_agent.py` from Anthropic SDK to OpenRouter via LiteLLM for cost-effective model selection.

## Changes Made

### 1. Dependency Updates
**File**: `requirements.txt`
- **Removed**: `anthropic==0.34.2`
- **Added**: `litellm==1.49.3`

### 2. Code Changes
**File**: `mindsdb_agent.py`

#### Imports (Lines 18-28)
- **Before**: Imported `anthropic` SDK with `Anthropic`, `TextBlock`, `ToolUseBlock`
- **After**: Imported `litellm.completion` function

#### Client Initialization (Lines 48-53)
- **Before**: Created Anthropic client with OpenRouter base URL
  ```python
  self.client = Anthropic(api_key=os.getenv('OPENROUTER_API_KEY'),
                          base_url="https://openrouter.ai/api/v1")
  ```
- **After**: Uses unified OpenRouter config for model selection
  ```python
  self.client = get_llm_client(task_type="analysis", temperature=0.7, max_tokens=4096)
  self.model = self.client.model
  ```

#### API Calls (Lines 176-183)
- **Before**: Used Anthropic's `messages.create()` API
- **After**: Uses LiteLLM's `completion()` function with OpenRouter models

#### Response Handling (Lines 200-210)
- **Before**: Parsed Anthropic response format with `ToolUseBlock` and `TextBlock`
- **After**: Uses standard OpenAI/LiteLLM response format with `choices[0].message`

#### Tool Call Format (Lines 217-282)
- **Before**: Anthropic's custom tool format
  ```python
  for tool_use in tool_uses:
      tool_use.name
      tool_use.input
      tool_use.id
  ```
- **After**: OpenAI-compatible tool call format
  ```python
  for tool_call in tool_calls:
      tool_call.function.name
      tool_call.function.arguments  # JSON string
      tool_call.id
  ```

#### Message Format (Lines 284-302)
- **Before**: Anthropic's message format with separate tool results
- **After**: OpenAI-compatible format with `tool_calls` and `role: "tool"` messages

## Benefits

### 1. Cost Savings
- Uses OpenRouter's cost-optimized model hierarchy
- Default task type "analysis" maps to **cheap tier** (Gemini Flash 1.5)
- Estimated cost: **~$0.10 per 1M tokens** vs Anthropic's $3.00/1M

### 2. Model Flexibility
- Easy switching between models via `task_type` parameter
- Automatic fallback to alternative models if primary fails
- Supports free, cheap, powerful, and reasoning tiers

### 3. Unified Configuration
- Single source of truth in `openrouter_config.py`
- Consistent model selection across all services
- Built-in rate limit handling and retries

## Model Selection
Based on `openrouter_config.py` task types:
- **database_validation**: Free tier (Llama 3.2 3B)
- **analysis**: Cheap tier (Gemini Flash 1.5) ← **Current usage**
- **research**: Powerful tier (Claude 3.5 Sonnet)
- **deep_reasoning**: Reasoning tier (DeepSeek)

## Testing

### Install Dependencies
```bash
cd service23
pip install -r requirements.txt
```

### Environment Variables Required
```bash
OPENROUTER_API_KEY=your_key_here
```

### Run Agent
```bash
# Interactive mode
python mindsdb_agent.py

# Single query
python mindsdb_agent.py "Show me some sample data"

# Without alerts
python mindsdb_agent.py --no-alerts "What's the success rate?"
```

### Expected Output
```
[*] API Keys Status:
  [+] OPENROUTER
  [-] OPENAI
  [-] ANTHROPIC
  [-] GOOGLE

[*] Using model: openrouter/google/gemini-flash-1.5
[*] Estimated cost: $0.1/1M tokens
```

## Backward Compatibility
**Breaking Changes**: None for users
- Same CLI interface
- Same functionality
- Same conversation format
- Only internal implementation changed

## Migration Checklist
- [x] Update imports (remove anthropic, add litellm)
- [x] Update client initialization
- [x] Update API call format
- [x] Update response parsing
- [x] Update tool call handling
- [x] Update message format
- [x] Update requirements.txt
- [x] Update docstrings
- [ ] Test with real MindsDB queries
- [ ] Verify tool calls work correctly
- [ ] Confirm conversation history maintains context

## Rollback Plan
If issues occur, revert to Anthropic SDK:
1. Restore `requirements.txt` (add back `anthropic==0.34.2`)
2. Restore original `mindsdb_agent.py` from git history
3. Run: `git checkout HEAD~1 mindsdb_agent.py requirements.txt`

## Next Steps
1. Install dependencies: `pip install -r requirements.txt`
2. Test with sample query
3. Monitor performance and costs
4. Consider upgrading to "powerful" tier for complex analysis if needed
