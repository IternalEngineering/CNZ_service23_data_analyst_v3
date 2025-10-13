# Ready-to-Use Curl Command

## The Command You Requested

```bash
curl -X POST http://localhost:8012/api/analyze/city-insights \
    -H "Content-Type: application/json" \
    -d '{
      "city": "Bristol",
      "country_code": "GB",
      "success_criteria": "Achieve net zero by 2030 through renewable energy"
    }'
```

## Before Running

1. **Start the API server**:
   ```bash
   python api_server.py
   ```

2. **Ensure database table exists**:
   ```bash
   python run_migration.py
   ```

## What Happens

1. Agent queries `service6_onboarding_voice.text_responses` for success criteria
2. Gathers city data from multiple tables (opportunities, data_sources, service19 data)
3. Claude agent connects the disparate data sources
4. Generates insights with recommendations
5. Stores in `service23_data_analyst_insights` table
6. Creates alert on web platform

## Expected Response

```json
{
  "success": true,
  "insight_id": "550e8400-e29b-41d4-a716-446655440000",
  "city": "Bristol",
  "country_code": "GB",
  "insight": {
    "insight_summary": "Bristol shows strong renewable energy potential...",
    "detailed_analysis": "Based on analysis of data from service6_onboarding_voice...",
    "data_sources_used": [
      "service6_onboarding_voice",
      "opportunities",
      "data_sources"
    ],
    "confidence_score": 0.85,
    "recommendations": [
      "Prioritize solar panel installations in south-facing areas",
      "Invest in wind energy infrastructure near coastal regions",
      "Implement smart grid technology for energy distribution"
    ]
  },
  "alert_created": true,
  "timestamp": "2025-10-09T12:34:56.789Z"
}
```

## Other Examples

### London
```bash
curl -X POST http://localhost:8012/api/analyze/city-insights \
    -H "Content-Type: application/json" \
    -d '{
      "city": "London",
      "country_code": "GB",
      "success_criteria": "Reduce carbon emissions by 50% by 2030"
    }'
```

### Bristol (auto-fetch success criteria from database)
```bash
curl -X POST http://localhost:8012/api/analyze/city-insights \
    -H "Content-Type: application/json" \
    -d '{
      "city": "Bristol",
      "country_code": "GB"
    }'
```

## Troubleshooting

**Connection refused**: API server not running
```bash
python api_server.py
```

**Table doesn't exist**: Run migration
```bash
python run_migration.py
```

**No data returned**: Check source tables have data for the city
```bash
python test_city_insights.py
```

## View Results in Database

```sql
SELECT * FROM service23_data_analyst_insights
WHERE city = 'Bristol'
ORDER BY created_at DESC
LIMIT 1;
```
