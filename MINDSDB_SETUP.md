# MindsDB Setup Guide

## Connection Configuration

Based on the MindsDB web interface test report, the following configuration has been verified as working:

### MindsDB Server (via SSH Tunnel)
- **EC2 Host**: 18.168.195.169
- **EC2 User**: ec2-user
- **SSH Key**: `C:\Users\chriz\.ssh\cnz-staging-key.pem`
- **Local URL**: http://localhost:47334 (tunneled from EC2)
- **Version**: 25.5.4.0
- **Authentication**: Disabled (local development)

## 🚀 Quick Start - SSH Tunnel Setup

### Step 1: Start SSH Tunnel

**Option A - Using PowerShell:**
```powershell
cd C:\Users\chriz\OneDrive\Documents\CNZ\UrbanZero2\UrbanZero\server_c
.\setup_tunnel.ps1
```

**Option B - Using Batch Script:**
```batch
cd C:\Users\chriz\OneDrive\Documents\CNZ\UrbanZero2\UrbanZero\server_c\research-agent
start_tunnel.bat
```

**Option C - Manual SSH Command:**
```bash
ssh -i C:\Users\chriz\.ssh\cnz-staging-key.pem -N -L 47334:localhost:47334 ec2-user@18.168.195.169
```

### Step 2: Verify Connection
```bash
curl http://localhost:47334/api/status
```

You should see:
```json
{
  "mindsdb_version": "25.5.4.0",
  "environment": "local",
  "auth": {"http_auth_enabled": false}
}
```

### Primary Datasource: urbanzero_postgres
- **Name**: `urbanzero_postgres`
- **Type**: PostgreSQL
- **Engine**: postgres
- **Host**: urbanzero-db.c5qeo4ayy5u5.eu-west-2.rds.amazonaws.com
- **Database**: urbanzero-db
- **SSL Mode**: require
- **Tables**: 54 tables available

## Available Tables

### Core Tables
- `cities` - City information (5 UK cities: Bristol, Manchester, Birmingham, Leeds, Edinburgh)
- `users` - User accounts
- `opportunities` - Investment opportunities
- `reports` - Generated reports

### SERVICE19 Tables (City Research Data)
- `service19_city_data` - City statistics and metrics
- `service19_data_sources` - Data source tracking
- `service19_search_results` - Search results cache

### AI & Integration Tables
- `ai_agents` - AI agent configurations
- `agent_data_flows` - Agent data flows
- `crew_execution_logs` - CrewAI execution logs
- `ckan_dataset_cache` - CKAN dataset cache

## Starting MindsDB

### Option 1: Python Module
```bash
python -m mindsdb
```

### Option 2: Direct Command
```bash
mindsdb
```

MindsDB will start on http://localhost:47334 by default.

## Testing Connection

### Using Python Script
```bash
cd research-agent
python test_mindsdb_quick.py
```

### Using MindsDB Client
```python
from mindsdb_client import MindsDBClient

client = MindsDBClient(host='localhost', port=47334, datasource='urbanzero_postgres')

# Test connection
if client.get_status():
    print("Connected to MindsDB")

# Get cities
cities = client.get_city_data()
print(cities)

# Search for a city
bristol = client.get_city_data(city_name='Bristol')
print(bristol)

# Get city statistics from SERVICE19
stats = client.get_city_statistics('Bristol')
print(stats)
```

## API Endpoints

### Status Check
```bash
curl http://localhost:47334/api/status
```

### List Databases
```bash
curl http://localhost:47334/api/databases/
```

### Execute SQL Query
```bash
curl -X POST http://localhost:47334/api/sql/query \
     -H "Content-Type: application/json" \
     -d '{"query": "SELECT * FROM urbanzero_postgres.cities LIMIT 5;"}'
```

## Example Queries

### List all tables
```sql
SHOW TABLES FROM urbanzero_postgres;
```

### Get all cities
```sql
SELECT * FROM urbanzero_postgres.cities;
```

### Get city by name
```sql
SELECT * FROM urbanzero_postgres.cities WHERE name = 'Bristol';
```

### Get SERVICE19 city data
```sql
SELECT * FROM urbanzero_postgres.service19_city_data WHERE city = 'Bristol';
```

### Get SERVICE19 data sources
```sql
SELECT * FROM urbanzero_postgres.service19_data_sources WHERE city = 'Bristol';
```

## Configuration in Code

The `mindsdb_client.py` has been configured with:
- **Default datasource**: `urbanzero_postgres`
- **Default host**: `localhost`
- **Default port**: `47334`
- **Table mappings**:
  - Cities: `urbanzero_postgres.cities`
  - Statistics: `urbanzero_postgres.service19_city_data`

## Troubleshooting

### MindsDB Not Running
```bash
# Check if MindsDB is running
curl http://localhost:47334/api/status

# If not running, start it
python -m mindsdb
```

### Connection Timeout
- Ensure MindsDB is running on port 47334
- Check firewall settings
- Verify no other service is using port 47334

### Database Not Found
- Verify datasource name is `urbanzero_postgres`
- Check datasource is connected: Visit http://localhost:47334 and check databases

### Empty Results
- Verify table exists: `SHOW TABLES FROM urbanzero_postgres`
- Check table has data: `SELECT COUNT(*) FROM urbanzero_postgres.cities`
- Verify query syntax matches PostgreSQL standards

## Integration with Research Agent

The MindsDB client is now integrated with the research agent workflow:

1. **City Search**: Uses `cities` table for city lookups
2. **City Statistics**: Uses `service19_city_data` for detailed metrics
3. **Data Sources**: Tracks sources in `service19_data_sources`
4. **Search Results**: Caches results in `service19_search_results`

All queries use real data from the PostgreSQL database - **no simulated data**.
