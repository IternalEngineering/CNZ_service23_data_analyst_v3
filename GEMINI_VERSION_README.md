# City Insights Analyzer - Gemini Version

## Overview

This is an alternative implementation of the City Insights Analyzer using **Google Gemini 1.5 Pro** instead of Claude. Created to avoid Claude's context limit errors while maintaining the same functionality.

## Key Differences from Claude Version

### Model
- **Claude Version**: Uses `claude-sonnet-4-5` with 200K context window
- **Gemini Version**: Uses `gemini-1.5-pro-latest` with **2M token context window** (10x larger)

### Benefits of Gemini Version
1. **Massive Context Window**: 2M tokens vs 200K tokens - can handle much larger conversations
2. **No Context Overflow**: Eliminates the context limit errors we were experiencing
3. **Cost Effective**: Generally lower cost per token than Claude
4. **Same Functionality**: Identical analysis capabilities and database operations

### Implementation Differences
- **Function Calling**: Uses Gemini's function calling format (similar but slightly different API)
- **Chat API**: Uses Gemini's chat sessions instead of Claude's messages API
- **Error Handling**: Adapted for Gemini-specific errors

## Files

### Core Files
- `city_insights_analyzer_gemini.py` - Main Gemini-based analyzer
- `test_city_insights_gemini.py` - Test script for Gemini version

### Dependencies
```bash
pip install google-generativeai
```

## Usage

### Command Line
```bash
# Same interface as Claude version
python city_insights_analyzer_gemini.py --city Bristol --country-code GB

# With success criteria
python city_insights_analyzer_gemini.py --city Bristol --country-code GB --success-criteria "Achieve net zero by 2030"

# Skip alert creation
python city_insights_analyzer_gemini.py --city Bristol --country-code GB --no-alert
```

### Test Script
```bash
python test_city_insights_gemini.py
```

### Python API
```python
from city_insights_analyzer_gemini import CityInsightsAnalyzerGemini

# Create analyzer
analyzer = CityInsightsAnalyzerGemini()

# Analyze and store
result = await analyzer.analyze_and_store(
    city="Bristol",
    country_code="GB",
    success_criteria="Achieve net zero by 2030",
    create_alert=True
)
```

## API Key

The Gemini API key is hardcoded in the class:
```python
api_key = "AIzaSyBKlZKkvDAjUv8SqcwIQ_ElWOgqlaaoD6Q"
```

You can override it by passing a different key to the constructor:
```python
analyzer = CityInsightsAnalyzerGemini(api_key="your-key-here")
```

## When to Use Gemini vs Claude

### Use Gemini When:
- ✅ Experiencing context limit errors with Claude
- ✅ Need to process very large amounts of data
- ✅ Want to reduce API costs
- ✅ Need longer conversation history

### Use Claude When:
- ✅ Want slightly better reasoning on complex tasks
- ✅ Already have existing Claude infrastructure
- ✅ Prefer Anthropic's approach to AI safety

## Schema Corrections

Both versions have been updated with the correct database schema:

### Correct Column Names
- `service6_onboarding_voice.text_responses` (NOT response_text)
- `service19_onboarding_agent_sources.search_city` (NOT city)
- `service19_onboarding_agent_sources.id` (NOT source_id as column name)
- `service19_onboarding_data.raw_data` (NOT data_content)
- `service19_onboarding_data.source_id` (foreign key to service19_onboarding_agent_sources.id)

## Database Tables

Both versions query these tables:
- `service6_onboarding_voice` - Success criteria and onboarding responses
- `service19_onboarding_agent_sources` - Source metadata with city info
- `service19_onboarding_data` - Collected city data with raw_data JSONB
- `opportunities` - Investment opportunities
- `data_sources` - Available data sources

Results are stored in:
- `service23_data_analyst_insights` - Generated insights with metadata

## Output Format

Both versions produce identical JSON output:
```json
{
  "success": true,
  "insight_id": "uuid",
  "city": "Bristol",
  "country_code": "GB",
  "insight": {
    "insight_summary": "Brief summary",
    "detailed_analysis": "Full analysis",
    "data_sources_used": ["table1", "table2"],
    "confidence_score": 0.85,
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  },
  "alert_created": true,
  "timestamp": "2025-10-11T..."
}
```

## Performance

### Context Handling
- **Claude Version**: Must aggressively prune conversation history (keeps last 6 messages)
- **Gemini Version**: Can maintain much longer conversation history without pruning

### Query Limits
Both versions enforce:
- Maximum 8 iterations
- LIMIT 5 on all SQL queries
- Result truncation to 5 rows max
- 3000 character limit on result strings

### Speed
- **First Response**: Similar (2-5 seconds)
- **With Many Queries**: Gemini may be slightly faster due to less context management overhead

## Error Handling

Both versions handle:
- Rate limits (with retry logic)
- Context overflow (Gemini version less likely to encounter)
- Database connection errors
- Malformed SQL queries (LIMIT clause enforcement)
- JSON parsing errors in responses

## Future Improvements

Potential enhancements for both versions:
1. Dynamic model selection based on task complexity
2. Automatic fallback from Claude to Gemini on context errors
3. Hybrid approach using both models for validation
4. Fine-tuned prompts optimized for each model's strengths

## Troubleshooting

### "google-generativeai not found"
```bash
pip install google-generativeai
```

### "API key invalid"
Check that the hardcoded API key is still valid or provide a new one.

### "Connection refused to database"
Ensure PostgreSQL credentials in `.env` are correct.

### Gemini-specific errors
Gemini errors are generally more descriptive than Claude's. Check the full traceback for details.

## Recommendation

**Use the Gemini version as the default** for City Insights analysis to avoid context limit issues. The Claude version remains available as a fallback if specific Claude features are needed.

## Related Files

- `city_insights_analyzer.py` - Original Claude-based version
- `test_city_insights.py` - Test for Claude version
- `postgres_direct_tool.py` - Shared database access
- `alert_creator.py` - Shared alert creation
